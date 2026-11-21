"""Scam awareness: transparent rule-based flags + Tavily research + Gemini explanation.
Never fetches the suspicious URL itself (avoids SSRF and malware risk) and never gives a definitive verdict."""
import re
from typing import List, Tuple

import config
from modules import gemini_service as G, scheme_search as S, validation as V
from utils.helpers import SHORTENERS, get_host, is_official_host, is_safe_url, now_ist

OFFICIAL_LINKS = ["https://cybercrime.gov.in/", "https://www.myscheme.gov.in/"]
SUSPICIOUS_TLDS = (".xyz", ".top", ".click", ".online", ".site", ".shop", ".icu", ".live", ".vip", ".work", ".buzz", ".cfd")
GOV_WORDS = ("yojana", "sarkari", "gov", "pmkisan", "pm-kisan", "scheme", "subsidy", "ayushman", "pension", "scholarship", "awas", "kisan", "mudra")
RULES = [
    ("Asks for advance payment or fee", "high", r"(registration|processing|application|activation|release)\s*(fee|charge)|pay\s*(rs|₹|inr)|deposit\s*(rs|₹)|₹\s*\d+\s*(to|for)\s*(register|apply|claim)",
     "Genuine government schemes do not ask citizens to pay agents or 'registration fees' to receive a benefit."),
    ("Asks for OTP, PIN, password or card/bank details", "high", r"\botp\b|\bpin\b|\bcvv\b|password|card number|net ?banking|upi pin|bank (details|account number)",
     "Government officials never ask for your OTP, PIN or password."),
    ("Guaranteed or unrealistic benefit", "high", r"guarantee|100\s*%|assured (benefit|amount)|free (laptop|phone|scooty|mobile|house)|₹\s*\d[\d,]*\s*(lakh|crore)|credited (immediately|instantly)|you (have )?(won|been selected)",
     "Real schemes have eligibility checks and cannot guarantee money to everyone who clicks a link."),
    ("Creates urgency or pressure", "medium", r"within\s*\d+\s*(hours?|hrs)|last date (is )?today|expires? (today|soon)|hurry|immediately|act now|limited (slots|seats)",
     "Scammers rush people so they do not stop to verify."),
    ("Asks to share the message or install an app/APK", "medium", r"forward (this|to)|share (with|to)\s*\d+|\.apk\b|install (the )?app",
     "Chain forwarding and unknown APK files are common in fraud campaigns."),
    ("Claims to be official but uses informal contact (WhatsApp/Telegram number)", "medium", r"whatsapp|telegram|wa\.me",
     "Official departments publish verified portals; they do not run schemes through private chat numbers."),
]


def heuristics(url: str, message: str) -> Tuple[List[V.ScamIndicator], str]:
    ind: List[V.ScamIndicator] = []
    host = get_host(url) if url.strip() else ""
    text = f"{message}\n{url}".lower()
    for name, sev, pat, why in RULES:
        if re.search(pat, text, re.I):
            ind.append(V.ScamIndicator(indicator=name, explanation=why, severity=sev))
    hosts = {host} | {get_host(m) for m in re.findall(r"(?:https?://|www\.)[^\s<>\"']+", message, re.I)}
    for h in filter(None, hosts):
        if h in SHORTENERS:
            ind.append(V.ScamIndicator(indicator=f"Shortened link ({h})", severity="high",
                       explanation="Short links hide the real destination. Official portals have clear gov.in / nic.in addresses."))
        elif not is_official_host(h):
            if any(w in h for w in GOV_WORDS):
                ind.append(V.ScamIndicator(indicator=f"Government-style name on a non-government domain ({h})", severity="high",
                           explanation="Official portals end with .gov.in or .nic.in. Look-alike domains often copy scheme names."))
            if h.endswith(SUSPICIOUS_TLDS):
                ind.append(V.ScamIndicator(indicator=f"Uncommon domain ending ({h})", severity="medium",
                           explanation="Cheap domain endings are frequently used in throw-away scam sites."))
            if "xn--" in h:
                ind.append(V.ScamIndicator(indicator="Look-alike (punycode) characters in domain", severity="high",
                           explanation="Special characters can imitate real website names."))
            if re.fullmatch(r"[\d.]+", h):
                ind.append(V.ScamIndicator(indicator="Link uses a raw IP address", severity="high", explanation="Legitimate portals use proper domain names."))
            if h.count("-") >= 3:
                ind.append(V.ScamIndicator(indicator="Many hyphens in domain name", severity="low", explanation="Long hyphenated names are common in impersonation sites."))
            if re.fullmatch(r"[\d.]+", h) and not is_safe_url("http://" + h):
                ind.append(V.ScamIndicator(indicator="Link points to a private/internal network address", severity="high",
                           explanation="Public government schemes never use internal addresses."))
    if url.strip().lower().startswith("http://"):
        ind.append(V.ScamIndicator(indicator="Connection is not encrypted (http)", severity="medium", explanation="Government portals use https."))
    return ind, host


def _level(ind: List[V.ScamIndicator], host: str, ai_risk: str = "") -> V.RiskLevel:
    score = sum({"low": 1, "medium": 2, "high": 3}[i.severity] for i in ind)
    high = any(i.severity == "high" for i in ind)
    if is_official_host(host) and not high and ai_risk != "high":
        return V.RiskLevel.OFFICIAL
    if score >= 5 or (high and ai_risk == "high"):
        return V.RiskLevel.HIGH
    if score >= 2 or ai_risk in ("medium", "high"):
        return V.RiskLevel.MEDIUM
    return V.RiskLevel.UNVERIFIED


BASE_ACTIONS = [
    "Do not pay any fee, share OTP/PIN/passwords, or click further links until you have verified.",
    "Check the scheme on the official portal https://www.myscheme.gov.in/ by typing the address yourself.",
    "If you already shared money or details, call the national cyber-crime helpline 1930 and report at https://cybercrime.gov.in/.",
    "Inform your bank immediately if bank or card details were shared.",
]


def analyze(url: str, message: str, lang: str) -> V.ScamAnalysis:
    url, message = (url or "").strip()[:500], (message or "").strip()[:4000]
    ind, host = heuristics(url, message)
    research: List[V.SourceDoc] = []
    notes = []
    if config.TAVILY_API_KEY:
        try:
            if host:
                research += S.tavily_search(f"{host} is it genuine official government website fraud", official_only=False, max_results=4)
            topic = message[:150] if message else (host or "")
            research += S.tavily_search(f"official government scheme {topic}", max_results=3)
        except S.SearchError as e:
            notes.append(str(e))
    ai_used, summary, actions, ai_risk = False, "", [], ""
    if G.available():
        try:
            ai = G.analyze_scam(url, message, [f"{i.indicator}: {i.explanation}" for i in ind], research, lang)
            ai_used, summary, actions, ai_risk = True, ai.summary, ai.recommended_actions, ai.risk.lower()
            have = {i.indicator.lower() for i in ind}
            ind += [i for i in ai.indicators if i.indicator.lower() not in have]
        except G.GeminiError as e:
            notes.append(str(e))
    level = _level(ind, host, ai_risk)
    if not summary:
        summary = {
            V.RiskLevel.HIGH: "This shows several warning signs commonly seen in scams. It could not be verified as official.",
            V.RiskLevel.MEDIUM: "This shows some warning signs and could not be verified as official.",
            V.RiskLevel.OFFICIAL: "The web address ends in an official government domain, but always type the address yourself and confirm it on myscheme.gov.in.",
            V.RiskLevel.UNVERIFIED: "No strong warning signs were found by the automatic checks, but this could not be verified as official.",
        }[level]
    summary += " " + " ".join(notes) if notes else ""
    return V.ScamAnalysis(risk_level=level, domain=host or None, summary=summary.strip(), indicators=ind,
                          recommended_actions=actions + [a for a in BASE_ACTIONS if a not in actions],
                          official_links=OFFICIAL_LINKS, research_sources=research[:6], ai_used=ai_used, analysed_at=now_ist())
