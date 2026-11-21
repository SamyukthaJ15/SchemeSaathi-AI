import ipaddress
import json
import re
import socket
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import config

IST = timezone(timedelta(hours=5, minutes=30))
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "rb.gy", "is.gd",
    "shorturl.at", "ow.ly", "tiny.cc", "buff.ly", "rebrand.ly", "t.ly",
}


def now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")


def get_host(url: str) -> str:
    try:
        u = url if "://" in url else "http://" + url
        return (urlparse(u).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def is_official_host(host: str) -> bool:
    return any(host == s or host.endswith("." + s) for s in config.OFFICIAL_SUFFIXES)


def is_http_url(url: str) -> bool:
    try:
        p = urlparse(url)
    except ValueError:
        return False
    return p.scheme in ("http", "https") and bool(p.hostname)


def is_safe_url(url: str) -> bool:
    """SSRF guard: http(s) only and the host must not resolve to a private/internal address.
    The app never fetches user-supplied URLs; this is used to flag internal targets."""
    if not is_http_url(url):
        return False
    host = urlparse(url).hostname
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def norm_url(url: str) -> str:
    return (url or "").strip().split("#")[0].rstrip("/").lower()


def clean_text(s: Any, limit: int = 2000) -> str:
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(s or ""))
    return s.strip()[:limit]


def extract_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating code fences and stray prose."""
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.I)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    starts = [i for i in (t.find("{"), t.find("[")) if i != -1]
    if not starts:
        raise ValueError("No JSON found")
    start = min(starts)
    end = max(t.rfind("}"), t.rfind("]"))
    try:
        return json.loads(t[start:end + 1])
    except json.JSONDecodeError as e:
        raise ValueError(str(e))
