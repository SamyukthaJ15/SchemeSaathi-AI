"""Gemini integration (google-genai SDK). All factual output is grounded in retrieved sources."""
import json
import time
from typing import List, Optional

import config
from modules import validation as V
from utils import prompts
from utils.helpers import extract_json, get_host, is_official_host, norm_url


class GeminiError(Exception):
    """User-presentable AI failure."""


_client = None


def available() -> bool:
    return bool(config.GEMINI_API_KEY)


def _lang(code: str) -> str:
    return config.LANGUAGES.get(code, ("", "English"))[1]


def _get_client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        _client = genai.Client(api_key=config.GEMINI_API_KEY, http_options=types.HttpOptions(timeout=35_000))
    return _client


def _generate(contents, system: Optional[str] = None, json_mode: bool = False, temperature: float = 0.2) -> str:
    if not available():
        raise GeminiError("Gemini API key is not configured.")
    from google.genai import types
    cfg = types.GenerateContentConfig(
        system_instruction=system, temperature=temperature,
        response_mime_type="application/json" if json_mode else "text/plain")
    
    # Ordered list of models to try in case the configured model is unavailable or busy
    candidates = []
    for m in [config.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
        if m and m not in candidates:
            candidates.append(m)

    last = None
    for model_name in candidates:
        for _ in range(2):
            try:
                resp = _get_client().models.generate_content(model=model_name, contents=contents, config=cfg)
                text = (resp.text or "").strip()
                if text:
                    return text
                last = GeminiError("empty")
            except Exception as e:  # network, quota, auth... never echo details that could include keys
                last = e
                err_str = str(e).lower()
                # If model is deprecated (404), deadline exceeded or high demand (503/504), fail fast to next candidate
                if "404" in err_str or "not_found" in err_str or "no longer available" in err_str or "503" in err_str or "504" in err_str:
                    break
                time.sleep(1.0)
    raise GeminiError(f"The AI service is temporarily unavailable ({type(last).__name__}). Please try again.")


def _json(prompt: str, system: Optional[str] = None, temperature: float = 0.2):
    for attempt in range(2):
        raw = _generate(prompt, system, json_mode=True, temperature=temperature)
        try:
            return extract_json(raw)
        except ValueError:
            prompt += "\n\nReturn ONLY valid JSON, no commentary."
    raise GeminiError("The AI returned a malformed response. Please try again.")


def _fill(template: str, **kw) -> str:
    for k, v in kw.items():
        template = template.replace(f"<<{k.upper()}>>", str(v))
    return template


# ---------------------------------------------------------------- recommendations
def recommend_schemes(profile_ai: dict, sources: List[V.SourceDoc]):
    """Returns (schemes, dropped_count). Schemes whose source_url was not actually retrieved are discarded."""
    data = _json(_fill(prompts.RECOMMEND, profile=json.dumps(profile_ai, ensure_ascii=False),
                       sources=prompts.format_sources(sources)), system=prompts.SYSTEM)
    raw = data.get("schemes", []) if isinstance(data, dict) else data
    by_url = {norm_url(d.url): d for d in sources}
    out, dropped, names = [], 0, set()
    for item in raw if isinstance(raw, list) else []:
        try:
            s = V.GovernmentScheme.model_validate(item)
        except V.ValidationError:
            dropped += 1
            continue
        doc = by_url.get(norm_url(s.source_url))
        if not doc or s.name.lower() in names:
            dropped += 1  # not grounded in a retrieved source, or duplicate
            continue
        names.add(s.name.lower())
        u = s.official_application_url
        if u and not (is_official_host(get_host(u)) or norm_url(u) in by_url):
            s.official_application_url = None
            s.verification_notes += " The application link suggested by the AI could not be confirmed, so it was removed."
        s.last_retrieved = doc.retrieved_at + (" (cached copy, not newly verified)" if doc.cached else "")
        s.is_demo = False
        if not doc.official:
            s.verification_notes += " Source is not a .gov.in/.nic.in website: treat as unverified."
        out.append(s)
    return out, dropped


def _explain(kind: str, scheme: V.GovernmentScheme, profile_ai: Optional[dict], lang: str) -> str:
    task = prompts.EXPLAIN[kind].replace("<<LANG>>", _lang(lang))
    prompt = _fill(prompts.EXPLAIN_WRAPPER, task=task, lang=_lang(lang),
                   scheme=scheme.model_dump_json(exclude={"is_demo"}),
                   profile=json.dumps(profile_ai or {}, ensure_ascii=False))
    return _generate(prompt, prompts.SYSTEM, temperature=0.3)


def explain_eligibility(scheme, profile_ai, lang): return _explain("eligibility", scheme, profile_ai, lang)
def explain_documents(scheme, profile_ai, lang): return _explain("documents", scheme, profile_ai, lang)
def explain_procedure(scheme, profile_ai, lang): return _explain("procedure", scheme, profile_ai, lang)


def summarize_source(doc: V.SourceDoc, lang: str) -> str:
    return _generate(_fill(prompts.SUMMARIZE, lang=_lang(lang), title=doc.title, url=doc.url, text=doc.content[:3000]),
                     prompts.SYSTEM, temperature=0.2)


# ---------------------------------------------------------------- language
def translate_json(payload: dict, lang: str) -> dict:
    data = _json(_fill(prompts.TRANSLATE_JSON, lang=_lang(lang), json=json.dumps(payload, ensure_ascii=False)), temperature=0)
    if not isinstance(data, dict):
        raise GeminiError("Translation failed.")
    return data


def translate_text(text: str, lang: str) -> str:
    return _generate(_fill(prompts.TRANSLATE_TEXT, lang=_lang(lang), text=text), temperature=0)


def transcribe_audio(data: bytes, mime: str = "audio/wav") -> str:
    from google.genai import types
    return _generate([types.Part.from_bytes(data=data, mime_type=mime), prompts.TRANSCRIBE], temperature=0).strip()


# ---------------------------------------------------------------- chatbot
def chat(question: str, profile_ai: Optional[dict], schemes: List[V.GovernmentScheme],
         sources: List[V.SourceDoc], history: list, lang: str) -> V.ChatResponse:
    brief = [{"name": s.name, "status": s.eligibility.status.value, "benefits": s.benefits[:2],
              "documents": [d.name for d in s.documents], "apply": s.official_application_url,
              "source": s.source_url} for s in schemes[:8]]
    hist = "\n".join(f"{m['role']}: {m['text'][:300]}" for m in history[-6:])
    data = _json(_fill(prompts.CHAT, profile=json.dumps(profile_ai or {}, ensure_ascii=False),
                       schemes=json.dumps(brief, ensure_ascii=False), sources=prompts.format_sources(sources, 1200, 5),
                       history=hist or "(none)", question=question[:1000], lang=_lang(lang)),
                 system=prompts.SYSTEM, temperature=0.3)
    try:
        resp = V.ChatResponse.model_validate(data)
    except V.ValidationError:
        raise GeminiError("The AI returned an unexpected answer format. Please rephrase and retry.")
    allowed = {norm_url(d.url) for d in sources} | {norm_url(s.source_url) for s in schemes}
    resp.sources = [u for u in resp.sources if norm_url(u) in allowed]
    return resp


# ---------------------------------------------------------------- scam analysis
def analyze_scam(url: str, message: str, flags: List[str], sources: List[V.SourceDoc], lang: str) -> V.ScamAIResult:
    data = _json(_fill(prompts.SCAM, url=url or "(none)", message=(message or "(none)")[:3000],
                       flags="\n".join(f"- {f}" for f in flags) or "(none)",
                       sources=prompts.format_sources(sources, 800, 5), lang=_lang(lang)),
                 system=prompts.SYSTEM, temperature=0.2)
    try:
        return V.ScamAIResult.model_validate(data)
    except V.ValidationError:
        raise GeminiError("The AI returned an unexpected answer format.")
