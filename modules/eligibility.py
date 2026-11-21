"""Orchestrates: validated profile -> Tavily retrieval -> Gemini analysis -> grounded, validated schemes."""
import config
from modules import demo_data, gemini_service as G, scheme_search as S, validation as V
from modules.profile import to_ai_dict
from utils.helpers import now_ist

ORDER = {V.EligibilityStatus.LIKELY: 0, V.EligibilityStatus.POSSIBLE: 1, V.EligibilityStatus.NOT: 2}


def _bundle(mode, schemes=None, sources=None, messages=None, dropped=0, error_detail=None):
    return dict(mode=mode, schemes=schemes or [], sources=sources or [], messages=messages or [],
                dropped=dropped, ran_at=now_ist(), error_detail=error_detail)


def _demo(profile, reason):
    schemes = demo_data.demo_schemes(profile)
    for s in schemes:
        s.is_demo = True
    return _bundle("demo", schemes, messages=[reason])


def find_schemes(profile: V.UserProfile) -> dict:
    if not config.live_ready():
        missing = [n for n, v in (("GEMINI_API_KEY", config.GEMINI_API_KEY), ("TAVILY_API_KEY", config.TAVILY_API_KEY)) if not v]
        reason = f"Missing API configuration: {', '.join(missing)}. Showing offline sample data."
        return _demo(profile, reason)

    # Step 1: Real-time search via Tavily
    try:
        sources, warnings = S.search_for_profile(profile)
    except S.SearchError as e:
        return _demo(profile, f"Live official search via Tavily failed: {e}. Falling back to sample data.")

    if not sources:
        return _bundle("empty", messages=warnings + ["No relevant official sources were found for this profile."])

    # Step 2: Live AI eligibility analysis via Gemini grounded in retrieved sources
    try:
        schemes, dropped = G.recommend_schemes(to_ai_dict(profile), sources)
    except G.GeminiError as e:
        # Partial API failure: Tavily succeeded with live official sources, but Gemini failed.
        # Provide sample schemes strictly marked as DEMO SAMPLE, while presenting live retrieved sources.
        demo_fallback = demo_data.demo_schemes(profile)
        for s in demo_fallback:
            s.is_demo = True
            s.verification_notes = f"Notice: Live AI analysis was unavailable ({e}). This is fallback sample data. Verify details on official portals."
        msg = f"Partial API Status: Live official government sources were successfully retrieved via Tavily, but live Gemini AI analysis failed ({e})."
        return _bundle("partial_tavily_only", schemes=demo_fallback, sources=sources,
                       messages=warnings + [msg], error_detail=str(e))

    for s in schemes:
        s.is_demo = False

    schemes.sort(key=lambda s: ORDER[s.eligibility.status])
    return _bundle("live", schemes=schemes, sources=sources, messages=warnings, dropped=dropped)
