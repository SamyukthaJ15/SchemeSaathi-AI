"""UI + content translation engine for SchemeSaathi AI with pre-compiled multilingual dictionary
and Gemini dynamic translation. Supports all 10 Indian languages in authentic native scripts."""
import streamlit as st

import config
from modules import gemini_service as G, validation as V

try:
    from modules import translations_data
    UI_TRANSLATIONS = getattr(translations_data, "UI_TRANSLATIONS", {})
    OPTIONS_TRANSLATIONS = getattr(translations_data, "OPTIONS_TRANSLATIONS", {})
    ABOUT_TRANSLATIONS = getattr(translations_data, "ABOUT_TRANSLATIONS", {})
except Exception:
    UI_TRANSLATIONS, OPTIONS_TRANSLATIONS, ABOUT_TRANSLATIONS = {}, {}, {}

UI = UI_TRANSLATIONS.get("en", {})


def current_lang() -> str:
    return st.session_state.get("lang", "en")


@st.cache_data(show_spinner=False, ttl=86400)
def _ui_translation(code: str) -> dict:
    if not G.available():
        return UI
    try:
        return G.translate_json(UI, code)
    except Exception:
        return UI


def prefetch():
    """Warm up state if needed."""
    code = current_lang()
    if code != "en" and code not in UI_TRANSLATIONS and G.available():
        _ui_translation(code)


def t(key: str, lang: str = None) -> str:
    """Translates a UI key into the current or specified language."""
    code = lang or current_lang()
    
    # 1. Check pre-compiled dictionary
    if code in UI_TRANSLATIONS and key in UI_TRANSLATIONS[code]:
        return UI_TRANSLATIONS[code][key]

    # 2. If English or missing API key, return base English
    base = UI.get(key, key)
    if code == "en" or not G.available():
        return base

    # 3. Dynamic cached translation fallback
    try:
        tr_map = _ui_translation(code)
        return tr_map.get(key) or base
    except Exception:
        return base


def t_opt(val: str, lang: str = None) -> str:
    """Translates a dropdown option value (e.g. 'Farmer' -> 'விவசாயி' in Tamil)."""
    if not val:
        return val
    code = lang or current_lang()
    if code in OPTIONS_TRANSLATIONS and val in OPTIONS_TRANSLATIONS[code]:
        return OPTIONS_TRANSLATIONS[code][val]
    return str(val)


def t_about(lang: str = None) -> str:
    """Returns the translated About markdown text in authentic native script."""
    code = lang or current_lang()
    if code in ABOUT_TRANSLATIONS:
        return ABOUT_TRANSLATIONS[code]
    return ABOUT_TRANSLATIONS.get("en", "")


def _strs(v, default):
    return [str(x) for x in v] if isinstance(v, list) and len(v) == len(default) else default


def translate_scheme(s: V.GovernmentScheme, code: str) -> V.GovernmentScheme:
    """Translate descriptive text only; official scheme name, department name, and URLs are preserved."""
    if code == "en" or not G.available():
        return s
    cache = st.session_state.setdefault("tr_cache", {})
    key = (s.name, s.source_url, code)
    if key in cache:
        return cache[key]

    payload = {
        "department": s.department,
        "description": s.description,
        "why_matches": s.why_matches,
        "requirements": s.eligibility.requirements,
        "matched_reasons": s.eligibility.matched_reasons,
        "missing_information": s.eligibility.missing_information,
        "benefits": s.benefits,
        "documents": [{"name": d.name, "notes": d.notes} for d in s.documents],
        "application_process": s.application_process,
        "verification_notes": s.verification_notes
    }
    try:
        tr = G.translate_json(payload, code)
    except G.GeminiError:
        return s

    n = s.model_copy(deep=True)
    n.department = str(tr.get("department") or s.department)
    n.description = str(tr.get("description") or s.description)
    n.why_matches = str(tr.get("why_matches") or s.why_matches)
    n.eligibility.requirements = _strs(tr.get("requirements"), s.eligibility.requirements)
    n.eligibility.matched_reasons = _strs(tr.get("matched_reasons"), s.eligibility.matched_reasons)
    n.eligibility.missing_information = _strs(tr.get("missing_information"), s.eligibility.missing_information)
    n.benefits = _strs(tr.get("benefits"), s.benefits)
    n.application_process = _strs(tr.get("application_process"), s.application_process)
    n.verification_notes = str(tr.get("verification_notes") or s.verification_notes)
    td = tr.get("documents")
    if isinstance(td, list) and len(td) == len(s.documents):
        for d, x in zip(n.documents, td):
            if isinstance(x, dict):
                d.name, d.notes = str(x.get("name") or d.name), str(x.get("notes") or d.notes)
    cache[key] = n
    return n
