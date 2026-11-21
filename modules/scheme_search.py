"""Tavily integration: real-time search with official-domain priority, timeouts and a small TTL cache."""
import time
from typing import List, Tuple

import requests

import config
from modules import validation as V
from utils.helpers import clean_text, get_host, is_http_url, is_official_host, now_ist

TAVILY_URL = "https://api.tavily.com/search"
OFFICIAL_DOMAINS = ["gov.in", "nic.in"]
_CACHE: dict = {}


class SearchError(Exception):
    """User-presentable search failure."""


def tavily_search(query: str, official_only: bool = True, max_results: int = 5) -> List[V.SourceDoc]:
    if not config.TAVILY_API_KEY:
        raise SearchError("Tavily API key is not configured.")
    ck = (query, official_only, max_results)
    hit = _CACHE.get(ck)
    if hit and time.time() - hit[0] < config.CACHE_TTL_SECONDS:
        # Served from cache: keep the ORIGINAL retrieval time and flag it, never present as fresh.
        return [d.model_copy(update={"cached": True}) for d in hit[1]]
    body = {"query": query, "search_depth": "basic", "max_results": max_results, "include_raw_content": True}
    if official_only:
        body["include_domains"] = OFFICIAL_DOMAINS
    try:
        r = requests.post(TAVILY_URL, json=body, timeout=config.HTTP_TIMEOUT,
                          headers={"Authorization": f"Bearer {config.TAVILY_API_KEY}"})
    except requests.Timeout:
        raise SearchError("The search service timed out. Please try again.")
    except requests.RequestException:
        raise SearchError("Could not reach the search service. Check your internet connection.")
    if r.status_code in (401, 403):
        raise SearchError("The Tavily API key was rejected. Check TAVILY_API_KEY in your .env file.")
    if r.status_code == 429:
        raise SearchError("Search rate limit reached. Please wait a moment and retry.")
    if not r.ok:
        raise SearchError(f"Search service error (HTTP {r.status_code}).")
    try:
        results = r.json().get("results", [])
    except ValueError:
        raise SearchError("The search service returned an unreadable response.")
    stamp, docs = now_ist(), []
    for it in results:
        url = (it.get("url") or "").strip()
        if not is_http_url(url):
            continue
        raw = (it.get("raw_content") or "").strip()
        docs.append(V.SourceDoc(
            title=clean_text(it.get("title") or url, 200), url=url,
            content=clean_text(raw or it.get("content") or "", 3000), retrieved_at=stamp,
            official=is_official_host(get_host(url)), has_full_text=bool(raw)))
    _CACHE[ck] = (time.time(), docs)
    return docs


def derive_categories(p: V.UserProfile) -> List[str]:
    c = []
    if p.age >= 60 or p.occupation == V.Occupation.RETIRED:
        c.append("senior citizen pension")
    if p.occupation == V.Occupation.STUDENT or p.education in (V.Education.HIGHER_SEC, V.Education.GRADUATE) and p.age <= 28:
        c.append("scholarship for students")
    if p.occupation in (V.Occupation.FARMER, V.Occupation.AG_LABOUR):
        c.append("farmer agriculture income support")
    if p.gender == V.Gender.FEMALE:
        c.append("women welfare")
    if p.disability == V.DisabilityStatus.YES:
        c.append("persons with disability")
    if p.annual_income <= 300000:
        c.append("housing and health insurance for low income families")
    if p.occupation == V.Occupation.SELF:
        c.append("self employed small business loan")
    if p.occupation in (V.Occupation.UNEMPLOYED, V.Occupation.DAILY):
        c.append("skill training employment")
    return c[:4] or ["welfare"]


def income_band(inc: int) -> str:
    for lim, label in ((100000, "below 1 lakh"), (300000, "1-3 lakh"), (600000, "3-6 lakh"), (900000, "6-9 lakh")):
        if inc < lim:
            return label
    return "above 9 lakh"


def age_group(age: int) -> str:
    return "child" if age < 18 else "youth" if age < 35 else "adult" if age < 60 else "senior citizen"


def search_for_profile(p: V.UserProfile) -> Tuple[List[V.SourceDoc], List[str]]:
    cats = derive_categories(p)
    qs = [f"central government scheme India {c} eligibility benefits documents how to apply" for c in cats[:2]]
    qs += [f"{p.state} state government scheme {c} eligibility benefits how to apply" for c in cats[:2]]
    qs.append(f"myscheme.gov.in {p.state} {p.occupation.value} {age_group(p.age)} income {income_band(p.annual_income)} schemes")
    seen, docs, warnings = set(), [], []
    for q in qs[:5]:
        try:
            for d in tavily_search(q):
                if d.url not in seen:
                    seen.add(d.url)
                    docs.append(d)
        except SearchError as e:
            warnings.append(str(e))
            if not docs and len(warnings) >= 2:
                raise
    if sum(d.official for d in docs) < 3:
        try:
            for d in tavily_search(f"{p.state} government schemes {cats[0]} official portal", official_only=False):
                if d.url not in seen:
                    seen.add(d.url)
                    docs.append(d)
        except SearchError as e:
            warnings.append(str(e))
    docs.sort(key=lambda d: not d.official)
    return docs[:10], warnings


def search_for_question(question: str, p) -> List[V.SourceDoc]:
    state = f" {p.state}" if p else ""
    return tavily_search(f"{question}{state} India government scheme", max_results=4)


def explore(state: str, category: str, keyword: str) -> List[V.SourceDoc]:
    parts = [keyword.strip(), "" if category == "All" else category, "scheme India eligibility how to apply"]
    if state and not state.startswith("All India"):
        parts.insert(0, state)
    docs = tavily_search(" ".join(x for x in parts if x), max_results=8)
    docs.sort(key=lambda d: not d.official)
    return docs
