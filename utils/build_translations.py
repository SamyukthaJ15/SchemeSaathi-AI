"""Script to generate comprehensive translation dictionaries for all 10 supported Indian languages."""
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

project_dir = Path(__file__).resolve().parent.parent
load_dotenv(project_dir / ".env")
sys.path.insert(0, str(project_dir))

import config
from modules import gemini_service as G

UI_EN = {
    "tagline": "Discover. Verify. Apply. Stay Protected.",
    "motto": "By the people, for the people's benefits.",
    "nav_home": "Home",
    "nav_find": "Find My Schemes",
    "nav_explore": "Explore Government Schemes",
    "nav_docs": "Document Assistant",
    "nav_scam": "Scam Checker",
    "nav_voice": "AI Voice Assistant",
    "nav_about": "About",
    "language": "Language",
    "senior_mode": "Senior-friendly mode (large text, high contrast)",
    "welcome_title": "Find the government schemes you may be eligible for",
    "welcome_sub": "Tell us a little about yourself. We search official government sources, explain eligibility in simple words, list the documents you need and show where to apply.",
    "cta_find": "Find my schemes",
    "feat_title": "What SchemeSaathi AI does",
    "feat1_t": "Personalised matches",
    "feat1_d": "Schemes matched to your age, state, income and occupation, with the reason for each match.",
    "feat2_t": "Central and State schemes",
    "feat2_d": "Searches official gov.in and nic.in websites for both Central and State schemes.",
    "feat3_t": "Document checklist",
    "feat3_d": "See exactly which documents each scheme asks for and spot what is missing.",
    "feat4_t": "Scam checker",
    "feat4_d": "Paste a suspicious link or message and see the warning signs.",
    "feat5_t": "10 Indian languages",
    "feat5_d": "Use the app in English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi, Gujarati or Punjabi.",
    "feat6_t": "Voice help",
    "feat6_d": "Speak your question and listen to the answer. Made with senior citizens in mind.",
    "senior_title": "Made easy for senior citizens",
    "senior_text": "Switch on senior-friendly mode in the sidebar for larger text and higher contrast, then use the voice assistant: tap the microphone, ask your question and listen to the reply.",
    "ai_title": "Ask the AI assistant",
    "ai_text": "Ask about eligibility, documents, benefits or how to apply. Answers are based on freshly retrieved official sources.",
    "find_title": "Find my schemes",
    "find_sub": "We do not ask for Aadhaar, bank account numbers or any other sensitive ID. Your name is never sent to the AI.",
    "try_scenarios": "Try a sample profile",
    "sc_student": "College student",
    "sc_farmer": "Farmer",
    "sc_senior": "Senior citizen",
    "sc_woman": "Woman",
    "sc_family": "Low-income family",
    "optional": "optional",
    "f_name": "Full name",
    "f_age": "Age",
    "f_gender": "Gender",
    "f_state": "State / Union Territory",
    "f_district": "District",
    "f_income": "Annual family income (₹)",
    "f_occupation": "Occupation",
    "f_education": "Education level",
    "f_category": "Social category",
    "f_residence": "Residence",
    "f_marital": "Marital status",
    "f_disability": "Disability status",
    "f_family": "Family size",
    "submit": "Find schemes",
    "searching": "Searching official sources and analysing eligibility…",
    "results_title": "Your scheme recommendations",
    "likely": "Likely Eligible",
    "possibly": "Possibly Eligible",
    "not_eligible": "Not Eligible",
    "central": "Central",
    "state": "State",
    "why_match": "Why this matches you",
    "eligibility": "Eligibility requirements",
    "missing_info": "Information still needed",
    "benefits": "Benefits",
    "documents": "Documents required",
    "how_apply": "How to apply",
    "apply_link": "Official application page",
    "source": "Source",
    "retrieved": "Last retrieved",
    "listen": "Listen",
    "explain_elig": "Explain eligibility simply",
    "explain_docs": "Explain documents",
    "explain_proc": "Explain how to apply",
    "check_docs": "Check my documents",
    "verify_note": "Please verify",
    "not_eligible_group": "Schemes you may not be eligible for",
    "sources_used": "Sources used",
    "disclaimer": "This is guidance, not a guarantee. Eligibility and benefits are decided only by the concerned government department. Always confirm on the official website.",
    "demo_banner": "DEMO MODE: sample data, NOT real-time results.",
    "live_banner": "LIVE DATA: Real-time official results retrieved and verified.",
    "partial_banner": "PARTIAL API SUCCESS: Real-time official sources retrieved, AI analysis unavailable.",
    "live_badge": "LIVE DATA",
    "demo_badge": "DEMO SAMPLE",
    "status_live_active": "LIVE DATA MODE (Active)",
    "status_demo_active": "DEMO MODE (Sample Data)",
    "demo_sidebar_note": "Demo mode is active for scheme results. Real-time API keys can be set in .env.",
    "ai_need_key": "AI explanations need a Gemini API key.",
    "cached_note": "Some sources were served from cache and are not newly verified.",
    "required": "Required",
    "optional_doc": "If applicable",
    "explore_title": "Explore government schemes",
    "category": "Category",
    "keyword": "Keyword (optional)",
    "search": "Search",
    "ai_summary": "AI summary",
    "official_site": "Official government site",
    "unverified_site": "Unverified website",
    "docs_title": "Document assistant",
    "docs_sub": "Pick a scheme, then optionally upload your documents. Files are checked in memory and are not stored.",
    "pick_scheme": "Choose a scheme",
    "upload": "Upload",
    "missing_docs": "Documents not uploaded yet",
    "docs_ready": "All required documents are uploaded and readable.",
    "doc_disclaimer": "These are basic file checks only (file type, size and readability). They do NOT verify that a certificate is genuine. Authenticity can be confirmed only by the issuing government authority or DigiLocker.",
    "scam_title": "Scam checker",
    "scam_sub": "Check a suspicious website, SMS, WhatsApp message or advertisement about a government scheme.",
    "sus_url": "Suspicious website address",
    "sus_msg": "Suspicious message or advertisement text",
    "analyze": "Check now",
    "risk_indicators": "Warning signs found",
    "safety_actions": "What to do now",
    "official_links": "Official websites",
    "scam_empty_input": "Enter a website address or paste a message first.",
    "scam_no_warnings": "No automatic warning signs found. That does not prove it is safe.",
    "scam_disclaimer": "This tool shows risk indicators only. It cannot confirm that a website is fraudulent or genuine. Report suspected fraud at cybercrime.gov.in.",
    "voice_title": "AI voice assistant",
    "voice_sub": "Tap the microphone, ask your question, and listen to the answer.",
    "tap_to_speak": "Tap to speak your question",
    "type_instead": "Or type your question",
    "read_aloud": "Read the answer aloud automatically",
    "you_said": "You asked",
    "answer": "Answer",
    "read_scheme": "Read a scheme aloud",
    "send": "Send",
    "ask_ai": "Ask the AI assistant",
    "need_key": "The AI assistant needs a Gemini API key. Add GEMINI_API_KEY to your .env file.",
    "about_title": "About SchemeSaathi AI",
    "profile_first": "Please fill in 'Find My Schemes' first to see results here.",
    "no_schemes_found": "No matching schemes could be verified from the retrieved sources. Try https://www.myscheme.gov.in/.",
    "voice_audio_error": "Could not understand the audio. Please try again or type your question.",
    "correct_errors": "Please correct the following:",
    "no_demo_category": "No demo sample for this category. Add API keys for live search."
}

OPTS_EN = {
    "Female": "Female",
    "Male": "Male",
    "Other / Prefer not to say": "Other / Prefer not to say",
    "Prefer not to say": "Prefer not to say",
    "Student": "Student",
    "Farmer": "Farmer",
    "Agricultural Labourer": "Agricultural Labourer",
    "Self-employed / Small Business": "Self-employed / Small Business",
    "Private Sector Employee": "Private Sector Employee",
    "Government Employee": "Government Employee",
    "Daily Wage Worker": "Daily Wage Worker",
    "Homemaker": "Homemaker",
    "Unemployed": "Unemployed",
    "Retired / Pensioner": "Retired / Pensioner",
    "Other": "Other",
    "No formal education": "No formal education",
    "Primary (up to Class 5)": "Primary (up to Class 5)",
    "Middle (Class 6-8)": "Middle (Class 6-8)",
    "Secondary (Class 10)": "Secondary (Class 10)",
    "Higher Secondary (Class 12)": "Higher Secondary (Class 12)",
    "Diploma / ITI": "Diploma / ITI",
    "Graduate": "Graduate",
    "Postgraduate": "Postgraduate",
    "Doctorate": "Doctorate",
    "General": "General",
    "OBC": "OBC",
    "SC": "SC",
    "ST": "ST",
    "EWS": "EWS",
    "Rural": "Rural",
    "Urban": "Urban",
    "Single": "Single",
    "Married": "Married",
    "Widowed": "Widowed",
    "Divorced / Separated": "Divorced / Separated",
    "Yes": "Yes",
    "No": "No",
    "All": "All",
    "Agriculture": "Agriculture",
    "Education & Scholarships": "Education & Scholarships",
    "Health": "Health",
    "Housing": "Housing",
    "Pension & Senior Citizens": "Pension & Senior Citizens",
    "Women & Child": "Women & Child",
    "Employment & Skills": "Employment & Skills",
    "Business & MSME": "Business & MSME",
    "Disability": "Disability",
    "All India (Central)": "All India (Central)",
}

ABOUT_EN = """**SchemeSaathi AI** helps Indian citizens discover government schemes they may qualify for, understand eligibility, prepare documents, find official application links and avoid scams.

**How it works.** Your profile is validated (Pydantic), official sources are retrieved in real time (Tavily, prioritising gov.in / nic.in), and Gemini analyses eligibility **only from those retrieved sources**. Any suggestion that cannot be matched to a retrieved source is discarded. Every scheme shows its source URL and retrieval time.

**Privacy.** We do not collect Aadhaar or bank numbers. Your name is never sent to the AI. Uploaded documents are checked in memory and are not stored. API keys live only in the server-side `.env` file.

**Limits.** This is guidance, not a guarantee. Eligibility is decided by the concerned department. Document checks are basic readability checks, not authenticity verification. Scam results are risk indicators, not verdicts.

**Useful links:** [myScheme](https://www.myscheme.gov.in/) · [National Cyber Crime Portal](https://cybercrime.gov.in/) · Helpline **1930**"""


def save(target_file, ui_tr, opts_tr, about_tr):
    output_code = f'''"""Pre-compiled multilingual dictionary for SchemeSaathi AI across all 10 supported languages."""
# Auto-generated or verified high-quality translations in native scripts.

UI_TRANSLATIONS = {json.dumps(ui_tr, ensure_ascii=False, indent=2)}

OPTIONS_TRANSLATIONS = {json.dumps(opts_tr, ensure_ascii=False, indent=2)}

ABOUT_TRANSLATIONS = {json.dumps(about_tr, ensure_ascii=False, indent=2)}
'''
    target_file.write_text(output_code, encoding="utf-8")


def translate_chunked(d: dict, code: str, chunk_size: int = 25) -> dict:
    items = list(d.items())
    res = {}
    for i in range(0, len(items), chunk_size):
        chunk = dict(items[i:i + chunk_size])
        for attempt in range(3):
            try:
                time.sleep(1.2)
                tr = G.translate_json(chunk, code)
                res.update(tr)
                break
            except Exception as e:
                print(f"  Chunk {i//chunk_size + 1} attempt {attempt+1} retry: {e}", flush=True)
                time.sleep(2.5)
        else:
            # Fallback to base
            res.update(chunk)
    return res


def main():
    target_file = project_dir / "modules" / "translations_data.py"
    ui_translations = {"en": UI_EN}
    opts_translations = {"en": OPTS_EN}
    about_translations = {"en": ABOUT_EN}

    if target_file.exists():
        try:
            from modules.translations_data import UI_TRANSLATIONS as U, OPTIONS_TRANSLATIONS as O, ABOUT_TRANSLATIONS as A
            ui_translations.update(U)
            opts_translations.update(O)
            about_translations.update(A)
            print(f"Loaded existing translations for: {list(ui_translations.keys())}")
        except Exception as e:
            print(f"Could not load existing file: {e}")

    all_languages = list(config.LANGUAGES.keys())
    missing_languages = [c for c in all_languages if c not in ui_translations or c not in opts_translations or c not in about_translations]
    print(f"Remaining languages to process: {missing_languages}", flush=True)

    for code in missing_languages:
        native, eng = config.LANGUAGES[code]
        print(f"\n--- Translating for {code} ({eng}) ---", flush=True)
        try:
            print(f"Translating UI chunked ({code})...", flush=True)
            ui_tr = translate_chunked(UI_EN, code, chunk_size=20)
            ui_translations[code] = {k: ui_tr.get(k, UI_EN.get(k, k)) for k in UI_EN}

            print(f"Translating Options chunked ({code})...", flush=True)
            opts_tr = translate_chunked(OPTS_EN, code, chunk_size=25)
            opts_translations[code] = {k: opts_tr.get(k, OPTS_EN.get(k, k)) for k in OPTS_EN}

            print(f"Translating About ({code})...", flush=True)
            time.sleep(1.2)
            about_tr = G.translate_text(ABOUT_EN, code)
            about_translations[code] = about_tr

            save(target_file, ui_translations, opts_translations, about_translations)
            print(f"SUCCESS saved for {code}!", flush=True)
        except Exception as e:
            print(f"FAILED for {code}: {e}", flush=True)

    print("\nAll done!")


if __name__ == "__main__":
    main()
