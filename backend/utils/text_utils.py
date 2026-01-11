import re
import unicodedata
from datetime import datetime

_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

CURRENCY_RE = re.compile(r"(₹|rs\.?|inr|\$|usd|eur|gbp)", re.IGNORECASE)

def normalize_text(text: str) -> str:
    """Normalize PDF extracted text for robust regex parsing."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # common pdf artifacts
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\r\n?", "\n", text)
    # collapse too many blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def safe_filename(s: str, max_len: int = 60) -> str:
    """Make a string safe for filenames."""
    if not s:
        return "UNKNOWN"
    s = normalize_text(s)
    s = s.replace("/", "-").replace("\\", "-")
    s = re.sub(r"[^A-Za-z0-9._ -]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    if not s:
        return "UNKNOWN"
    return s[:max_len]

def _to_int(x: str, default=None):
    try:
        return int(x)
    except Exception:
        return default

def normalize_date(raw: str) -> str:
    if not raw:
        return "UNKNOWN"

    s = raw.strip()

    # already normalized
    if re.fullmatch(r"\d{4}_\d{2}_\d{2}", s):
        return s

    # try formats like 2025-12-18 or 2025/12/18
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}_{mo:02d}_{d:02d}"

    # try formats like 18/12/2025 or 18-12-2025
    m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}_{mo:02d}_{d:02d}"

    # try "18 November 2025" / "28 Nov 2025"
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
    if m:
        d = int(m.group(1))
        mon_txt = m.group(2).strip().lower()
        y = int(m.group(3))
        mon = _MONTHS.get(mon_txt, _MONTHS.get(mon_txt[:3]))
        if mon:
            return f"{y:04d}_{mon:02d}_{d:02d}"

    return "UNKNOWN"

def extract_money_candidates(text: str):
    """
    Returns list of tuples (value_float, raw_match, context_line)
    Handles ₹719.35, Rs 1,234.00, INR 719, 719.35 etc (when near Total lines).
    """
    if not text:
        return []

    candidates = []
    lines = [ln.strip() for ln in normalize_text(text).splitlines() if ln.strip()]

    # money regex (allow commas)
    money_re = re.compile(r"(?:(₹|rs\.?|inr|\$)\s*)?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)", re.IGNORECASE)

    for ln in lines:
        for m in money_re.finditer(ln):
            sym = m.group(1) or ""
            amt = m.group(2)
            # ignore short plain numbers unless currency symbol exists or line has total keyword
            if not sym and not re.search(r"\b(total|amount|paid|grand|net|balance)\b", ln, re.I):
                continue

            num = float(amt.replace(",", ""))
            # ignore tiny numbers that are likely item qty or taxes percentages
            if num < 1:
                continue
            candidates.append((num, (sym + amt).strip(), ln))
    return candidates
