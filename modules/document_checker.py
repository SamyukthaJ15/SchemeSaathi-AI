"""Basic upload checks (type, size, readability). This is NOT certificate authentication."""
import io
from typing import List, Optional

import config

MAGIC = {"pdf": [b"%PDF"], "png": [b"\x89PNG"], "jpg": [b"\xff\xd8\xff"], "jpeg": [b"\xff\xd8\xff"]}
ALLOWED = list(MAGIC)
DISCLAIMER = ("These are basic file checks only (file type, size and readability). They do NOT verify that a certificate "
              "is genuine. Authenticity can be confirmed only by the issuing government authority or an authorised "
              "verification service such as DigiLocker.")


def check_file(name: str, data: bytes) -> dict:
    """Returns {ok, issues, notes}. Files are inspected in memory only and never written to disk."""
    issues: List[str] = []
    notes: List[str] = []
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED:
        return dict(ok=False, issues=[f"Unsupported file type. Allowed: {', '.join(ALLOWED)}."], notes=[])
    if len(data) == 0:
        return dict(ok=False, issues=["The file is empty."], notes=[])
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        return dict(ok=False, issues=[f"File is larger than {config.MAX_UPLOAD_MB} MB."], notes=[])
    if not any(data.startswith(m) for m in MAGIC[ext]):
        return dict(ok=False, issues=["File content does not match its extension."], notes=[])
    try:
        if ext == "pdf":
            _check_pdf(data, issues, notes)
        else:
            _check_image(data, issues, notes)
    except Exception:
        issues.append("The file could not be opened. It may be corrupted.")
    return dict(ok=not issues, issues=issues, notes=notes)


def _check_pdf(data, issues, notes):
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(data))
    if r.is_encrypted:
        issues.append("PDF is password-protected and cannot be read.")
        return
    n = len(r.pages)
    notes.append(f"PDF opened successfully ({n} page{'s' if n != 1 else ''}).")
    text = "".join((r.pages[i].extract_text() or "") for i in range(min(n, 3))).strip()
    notes.append("Readable text found." if len(text) > 20 else
                 "No machine-readable text (common for scanned documents). Make sure the scan is clear.")


def _check_image(data, issues, notes):
    from PIL import Image, ImageStat
    Image.MAX_IMAGE_PIXELS = 50_000_000
    img = Image.open(io.BytesIO(data))
    img.verify()
    img = Image.open(io.BytesIO(data))
    w, h = img.size
    notes.append(f"Image opened successfully ({w}×{h}px).")
    if min(w, h) < 400:
        issues.append("Image resolution is very low; text may be unreadable. Retake with better light.")
    if ImageStat.Stat(img.convert("L")).stddev[0] < 8:
        issues.append("Image looks blank or has very low contrast.")


def missing_documents(required: List[str], provided: List[str]) -> List[str]:
    return [d for d in required if d not in provided]
