# SchemeSaathi AI
*By the people, for the people's benefits.*  ·  Discover. Verify. Apply. Stay Protected.

AI-powered discovery of Indian Central & State government schemes (Streamlit + Gemini + Tavily + Pydantic + gTTS).

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then add GEMINI_API_KEY and TAVILY_API_KEY
streamlit run app.py
```
Keys: Gemini → https://aistudio.google.com/apikey · Tavily → https://app.tavily.com
Without keys the app starts in a clearly labelled **demo mode** (sample data, not real-time).

## How grounding works
1. Profile validated by Pydantic (`modules/validation.py`); name is never sent to AI.
2. `scheme_search.py` queries Tavily (gov.in / nic.in first), keeps URL + retrieval time, caches for 1 hour and labels cached results.
3. `gemini_service.recommend_schemes` sees only the retrieved sources; output is validated and **any scheme whose `source_url` was not retrieved is discarded**; unverifiable apply-links are removed.
4. UI shows source, retrieval time, missing information and a verification disclaimer for every scheme.

## Sample scenarios
Buttons on *Find My Schemes*: college student, farmer, senior citizen (Tamil Nadu), woman, low-income family.
Voice example: "My age is 65. I live in Tamil Nadu. What pension schemes can I apply for?"

## Notes
- Speech-to-text uses Gemini audio understanding (`st.audio_input`, Streamlit ≥ 1.40); `SpeechRecognition` is an optional fallback.
- Text-to-speech (gTTS) needs internet access.
- Uploaded documents are checked in memory only. Checks are readability checks, not authenticity verification.
- The scam checker never opens the suspicious URL; it reports risk indicators, never a definitive verdict.
- Form dropdown options stay in English so validation is exact; all other UI and scheme content follows the selected language.
