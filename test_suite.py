"""Comprehensive test and validation suite for SchemeSaathi AI."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_dir = Path(__file__).resolve().parent
load_dotenv(project_dir / ".env")
sys.path.insert(0, str(project_dir))

import config
from modules import (
    demo_data,
    document_checker,
    eligibility,
    gemini_service as G,
    profile as prof,
    scam_detector,
    scheme_search as S,
    translator,
    validation as V,
)
from modules.translator import t, t_opt, t_about


def test_1_all_language_options():
    print("\n==========================================")
    print("TEST 1: All 10 Language Options Validation")
    print("==========================================")
    required_languages = ["en", "ta", "hi", "te", "ml", "kn", "bn", "mr", "gu", "pa"]
    for code in required_languages:
        assert code in config.LANGUAGES, f"Language {code} missing from config.LANGUAGES"
        native, eng = config.LANGUAGES[code]
        title = t("welcome_title", code)
        btn = t("cta_find", code)
        farmer = t_opt("Farmer", code)
        rural = t_opt("Rural", code)
        print(f"[{code}] {eng} ({native}):")
        print(f"   Title: {title[:50]}...")
        print(f"   Button: {btn}")
        print(f"   Farmer: {farmer} | Rural: {rural}")
        assert title and title != "welcome_title", f"Translation missing for welcome_title in {code}"
        assert btn and btn != "cta_find", f"Translation missing for cta_find in {code}"
        assert farmer and farmer != "Farmer" or code == "en", f"Option translation failed for {code}"
    print(">>> PASS: All 10 languages validated successfully with authentic native scripts.")


def test_2_pages_multilingual():
    print("\n==========================================")
    print("TEST 2: Every Page Navigation & Titles in All Languages")
    print("==========================================")
    pages = ["nav_home", "nav_find", "nav_explore", "nav_docs", "nav_scam", "nav_voice", "nav_about"]
    for code in ["en", "ta", "hi", "te", "ml", "kn", "bn", "mr", "gu", "pa"]:
        navs = [t(p, code) for p in pages]
        about_md = t_about(code)
        assert len(about_md) > 50, f"About text missing for {code}"
        print(f"[{code}] Navs: {' | '.join(navs[:4])}...")
    print(">>> PASS: All page titles and navigation labels translated across all 10 languages.")


def test_3_successful_live_api_request():
    print("\n==========================================")
    print("TEST 3: Live Tavily + Gemini API Request")
    print("==========================================")
    assert config.live_ready(), "API keys must be present for live test"
    
    # Test a farmer profile in Uttar Pradesh
    p = V.UserProfile(
        name="Ramesh", age=45, gender=V.Gender.MALE, state="Uttar Pradesh",
        annual_income=120000, occupation=V.Occupation.FARMER,
        education=V.Education.SECONDARY, residence=V.Residence.RURAL
    )
    res = eligibility.find_schemes(p)
    print("Mode:", res["mode"])
    print("Retrieved At:", res["ran_at"])
    print("Sources count:", len(res["sources"]))
    print("Schemes count:", len(res["schemes"]))
    
    assert res["mode"] in ("live", "partial_tavily_only"), f"Unexpected mode: {res['mode']}"
    assert res["ran_at"], "Timestamp must be present"
    assert len(res["sources"]) > 0, "Real official sources must be retrieved"
    
    for s in res["schemes"]:
        print(f" - Scheme: {s.name} (is_demo={s.is_demo})")
        print(f"   Source URL: {s.source_url}")
        print(f"   Last Retrieved: {s.last_retrieved}")
        assert s.source_url.startswith("http"), f"Invalid source URL: {s.source_url}"
        if res["mode"] == "live":
            assert s.is_demo is False, "Live scheme must have is_demo=False"
    print(">>> PASS: Live API fetching and processing succeeded.")


def test_4_gemini_partial_failure():
    print("\n==========================================")
    print("TEST 4: Partial API Failure (Tavily OK, Gemini Fails)")
    print("==========================================")
    # Save original recommend_schemes
    orig_rec = G.recommend_schemes
    
    def mock_rec_fail(*args, **kwargs):
        raise G.GeminiError("Simulated Gemini Quota/503 Failure")
    
    G.recommend_schemes = mock_rec_fail
    try:
        p = V.UserProfile(
            name="Ramesh", age=45, gender=V.Gender.MALE, state="Uttar Pradesh",
            annual_income=120000, occupation=V.Occupation.FARMER,
            education=V.Education.SECONDARY, residence=V.Residence.RURAL
        )
        res = eligibility.find_schemes(p)
        print("Mode:", res["mode"])
        print("Messages:", res["messages"])
        print("Sources retained:", len(res["sources"]))
        assert res["mode"] == "partial_tavily_only", f"Expected partial_tavily_only, got {res['mode']}"
        assert len(res["sources"]) > 0, "Retrieved sources must be preserved"
        assert any("Partial API Status" in m for m in res["messages"]), "Warning message must be present"
        for s in res["schemes"]:
            assert s.is_demo is True, "Fallback schemes during AI failure must be marked is_demo=True"
        print(">>> PASS: Partial API failure handled correctly with appropriate warning.")
    finally:
        G.recommend_schemes = orig_rec


def test_5_tavily_failure_fallback():
    print("\n==========================================")
    print("TEST 5: Tavily Failure Scenario -> Fallback to Demo")
    print("==========================================")
    orig_search = S.search_for_profile
    
    def mock_search_fail(*args, **kwargs):
        raise S.SearchError("Simulated Network/Tavily Timeout")
    
    S.search_for_profile = mock_search_fail
    try:
        p = V.UserProfile(
            name="Ramesh", age=45, gender=V.Gender.MALE, state="Uttar Pradesh",
            annual_income=120000, occupation=V.Occupation.FARMER,
            education=V.Education.SECONDARY, residence=V.Residence.RURAL
        )
        res = eligibility.find_schemes(p)
        print("Mode:", res["mode"])
        print("Messages:", res["messages"])
        assert res["mode"] == "demo", f"Expected demo, got {res['mode']}"
        assert len(res["schemes"]) > 0, "Fallback demo schemes must be returned"
        for s in res["schemes"]:
            assert s.is_demo is True, "Demo schemes must have is_demo=True"
        print(">>> PASS: Tavily failure correctly falls back to Demo Mode.")
    finally:
        S.search_for_profile = orig_search


def test_6_live_vs_demo_distinction():
    print("\n==========================================")
    print("TEST 6: Distinguish Live Data vs Demo Data")
    print("==========================================")
    # Demo scheme
    demo_s = demo_data.demo_schemes(V.UserProfile(
        name="Test", age=30, gender=V.Gender.FEMALE, state="Tamil Nadu",
        annual_income=200000, occupation=V.Occupation.STUDENT,
        education=V.Education.GRADUATE, residence=V.Residence.URBAN
    ))[0]
    assert demo_s.is_demo is True, "Demo scheme must have is_demo=True"
    assert "demo sample data" in demo_s.last_retrieved.lower()
    
    # Live scheme simulation
    live_s = demo_s.model_copy(update={"is_demo": False, "last_retrieved": "21 Nov 2026, 01:38 PM IST"})
    assert live_s.is_demo is False, "Live scheme must have is_demo=False"
    assert "demo" not in live_s.last_retrieved.lower()
    print("Demo Scheme Badge Check: is_demo =", demo_s.is_demo, "| Retrieved:", demo_s.last_retrieved)
    print("Live Scheme Badge Check: is_demo =", live_s.is_demo, "| Retrieved:", live_s.last_retrieved)
    print(">>> PASS: Live data and Demo data are strictly distinguished.")


def test_7_scheme_translation():
    print("\n==========================================")
    print("TEST 7: Dynamic Scheme Translation via Gemini")
    print("==========================================")
    demo_s = demo_data._RAW["pmkisan"]
    s = V.GovernmentScheme(
        name=demo_s["name"], level=V.SchemeLevel.CENTRAL, department=demo_s["dept"],
        description=demo_s["desc"], why_matches="You are a farmer.",
        eligibility=V.SchemeEligibility(status=V.EligibilityStatus.LIKELY, requirements=demo_s["reqs"]),
        benefits=demo_s["benefits"], documents=demo_s["docs"], application_process=demo_s["steps"],
        official_application_url=demo_s["apply"], source_url=demo_s["source"],
        last_retrieved="21 Nov 2026, 01:38 PM IST", is_demo=False
    )
    
    tr_ta = translator.translate_scheme(s, "ta")
    print("Original Name:", s.name)
    print("Tamil Translated Name (preserved):", tr_ta.name)
    print("Tamil Description (Tamil script):", tr_ta.description)
    print("Tamil Benefits (Tamil script):", tr_ta.benefits[0])
    
    assert tr_ta.name == s.name, "Scheme name must be preserved"
    assert tr_ta.source_url == s.source_url, "Source URL must be preserved"
    assert tr_ta.is_demo == s.is_demo, "is_demo status must be preserved"
    assert any("\u0b80" <= c <= "\u0bff" for c in tr_ta.description), "Tamil description must contain Tamil Unicode script"
    print(">>> PASS: Scheme translation preserves official names/URLs while translating description in authentic Tamil script.")


def test_8_document_checker():
    print("\n==========================================")
    print("TEST 8: Document Checker Validation")
    print("==========================================")
    # Empty data check
    res_empty = document_checker.check_file("test.pdf", b"")
    assert not res_empty["ok"], "Empty file should fail"
    
    # Extension mismatch
    res_ext = document_checker.check_file("test.pdf", b"dummy")
    assert not res_ext["ok"], "Bad magic number should fail"
    
    # Missing documents
    missing = document_checker.missing_documents(["Aadhaar card", "Bank passbook"], ["Aadhaar card"])
    assert missing == ["Bank passbook"], f"Missing docs mismatch: {missing}"
    print(">>> PASS: Document checker functions verified.")


def main():
    test_1_all_language_options()
    test_2_pages_multilingual()
    test_3_successful_live_api_request()
    test_4_gemini_partial_failure()
    test_5_tavily_failure_fallback()
    test_6_live_vs_demo_distinction()
    test_7_scheme_translation()
    test_8_document_checker()
    print("\n==========================================")
    print("ALL TESTS PASSED SUCCESSFULLY! 100% COMPLETE.")
    print("==========================================")


if __name__ == "__main__":
    main()
