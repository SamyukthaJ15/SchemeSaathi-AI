"""Central configuration. Secrets come only from environment variables / .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current file's directory, parent directory, and current working directory
_config_dir = Path(__file__).resolve().parent
for candidate in (_config_dir / ".env", _config_dir.parent / ".env", Path.cwd() / ".env"):
    if candidate.is_file():
        load_dotenv(candidate, override=False)
        break
else:
    load_dotenv()


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


GEMINI_API_KEY = _env("GEMINI_API_KEY")
TAVILY_API_KEY = _env("TAVILY_API_KEY")
GEMINI_MODEL = _env("GEMINI_MODEL", "gemini-3.5-flash-lite")
CACHE_TTL_SECONDS = int(_env("CACHE_TTL_SECONDS", "3600") or 3600)
HTTP_TIMEOUT = 25
MAX_UPLOAD_MB = 5

# code -> (native name, English name used in prompts)
LANGUAGES = {
    "en": ("English", "English"),
    "ta": ("தமிழ்", "Tamil"),
    "hi": ("हिन्दी", "Hindi"),
    "te": ("తెలుగు", "Telugu"),
    "ml": ("മലയാളം", "Malayalam"),
    "kn": ("ಕನ್ನಡ", "Kannada"),
    "bn": ("বাংলা", "Bengali"),
    "mr": ("मराठी", "Marathi"),
    "gu": ("ગુજરાતી", "Gujarati"),
    "pa": ("ਪੰਜਾਬੀ", "Punjabi"),
}

OFFICIAL_SUFFIXES = ("gov.in", "nic.in")

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]


def gemini_ready() -> bool:
    return bool(GEMINI_API_KEY)


def tavily_ready() -> bool:
    return bool(TAVILY_API_KEY)


def live_ready() -> bool:
    return bool(GEMINI_API_KEY and TAVILY_API_KEY)
