"""Text-to-speech (gTTS) and speech-to-text (Gemini audio understanding, SpeechRecognition fallback)."""
import io
import re

import streamlit as st

from modules import gemini_service as G, validation as V

BCP47 = {"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN", "te": "te-IN", "ml": "ml-IN",
         "kn": "kn-IN", "bn": "bn-IN", "mr": "mr-IN", "gu": "gu-IN", "pa": "pa-IN"}


def clean_for_speech(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_`#>|]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:2500]


@st.cache_data(show_spinner=False, max_entries=40, ttl=3600)
def tts_bytes(text: str, lang: str) -> bytes:
    from gtts import gTTS
    buf = io.BytesIO()
    gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
    return buf.getvalue()


def play(text: str, lang: str, autoplay: bool = False) -> None:
    """Shows a native audio player (play / pause / seek)."""
    clean = clean_for_speech(text)
    if not clean:
        return
    try:
        st.audio(tts_bytes(clean, lang), format="audio/mp3", autoplay=autoplay)
    except Exception:
        st.warning("Audio could not be created. Text-to-speech needs an internet connection.")


def transcribe(audio_bytes: bytes, lang: str) -> str:
    if G.available():
        try:
            return G.transcribe_audio(audio_bytes)
        except G.GeminiError:
            pass
    try:  # optional fallback: pip install SpeechRecognition
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as src:
            audio = r.record(src)
        return r.recognize_google(audio, language=BCP47.get(lang, "en-IN"))
    except Exception:
        return ""


def scheme_speech(s: V.GovernmentScheme, section: str, heading: str = "") -> str:
    """Builds the text to read aloud. `s` should already be in the selected language."""
    head = f"{s.name}. {heading}. " if heading else f"{s.name}. "
    if section == "eligibility":
        return head + " ".join(s.eligibility.requirements)
    if section == "benefits":
        return head + " ".join(s.benefits)
    if section == "documents":
        return head + ", ".join(d.name for d in s.documents)
    if section == "steps":
        return head + " ".join(f"{i}. {x}" for i, x in enumerate(s.application_process, 1))
    return f"{s.name}. {s.description} {s.why_matches}"
