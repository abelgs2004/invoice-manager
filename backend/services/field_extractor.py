import re
from backend.utils.text_utils import normalize_text, normalize_date, extract_money_candidates

STOP_VENDOR_WORDS = {
    "tax", "taxes", "gst", "cgst", "sgst", "igst", "invoice", "receipt", "bill",
    "order", "summary", "payment", "paid", "total", "amount", "date",
    "customer", "name", "address", "delivery", "platform", "fee"
}

ADDRESS_HINTS = {"street", "st.", "road", "rd", "layout", "nagar", "floor", "building", "bengaluru", "bangalore", "india", "pin", "pincode"}

TOTAL_KEYS = [
    "grand total",
    "total amount",
    "amount paid",
    "total paid",
    "net payable",
    "net amount",
    "total",
    "balance due",
]

BAD_TOTAL_CONTEXT = [
    "tax", "taxes", "gst", "cgst", "sgst", "igst",
    "discount", "promo", "coupon",
    "tip", "delivery", "platform fee", "packaging", "service charge",
    "subtotal",
]

DATE_KEYS = [
    "invoice date",
    "bill date",
    "order time",
    "order date",
    "date",
]

def _clean_vendor(line: str) -> str:
    line = re.sub(r"[^A-Za-z0-9 &()._-]+", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line

def _vendor_score(line: str) -> float:
    """
    Score a line as a vendor candidate.
    We want "California Burrito" not address, not labels, not customer name.
    """
    s = line.strip()
    if not s:
        return -999

    low = s.lower()

    # reject if it's a label-like line
    if ":" in s and len(s) < 35:
        return -50

    # reject address-ish lines
    if any(w in low for w in ADDRESS_HINTS):
        return -30

    # reject if contains too many digits
    digit_ratio = sum(ch.isdigit() for ch in s) / max(1, len(s))
    if digit_ratio > 0.25:
        return -25

    # reject stop words dominating
    tokens = re.findall(r"[a-zA-Z]+", low)
    if tokens:
        stop_hits = sum(1 for t in tokens if t in STOP_VENDOR_WORDS)
        if stop_hits / max(1, len(tokens)) > 0.5:
            return -20

    # basic preference
    score = 0
    if 3 <= len(s) <= 40:
        score += 10
    if re.search(r"[A-Za-z]", s):
        score += 5
    if re.search(r"\b(pvt|ltd|limited|inc|llp|store|restaurant|cafe|hotel)\b", low):
        score += 8
    # Title-case / upper-ish is common for vendor names
    upper_ratio = sum(ch.isupper() for ch in s if ch.isalpha()) / max(1, sum(ch.isalpha() for ch in s))
    if upper_ratio > 0.5:
        score += 5

    return score

def extract_vendor(text: str) -> str:
    """
    Practical vendor extraction:
      - Prefer top-of-document lines (first ~20 non-empty lines).
      - Pick the highest-scoring line.
      - Avoid customer name / address / labels.
    """
    if not text:
        return "UNKNOWN"
    t = normalize_text(text)
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    # take the very top chunk
    top = lines[:25]

    # also consider "Restaurant Name:", "Merchant:", etc
    explicit_patterns = [
        r"\b(restaurant name|merchant|sold by|store|vendor)\s*:\s*(.+)$",
        r"\b(billed from)\s*:\s*(.+)$",
    ]
    for ln in top:
        for pat in explicit_patterns:
            m = re.search(pat, ln, re.I)
            if m:
                cand = _clean_vendor(m.group(len(m.groups())))
                if cand and len(cand) >= 3:
                    return cand

    best = ("UNKNOWN", -999)
    for ln in top:
        cand = _clean_vendor(ln)
        sc = _vendor_score(cand)
        if sc > best[1]:
            best = (cand, sc)

    return best[0] if best[1] >= 5 else "UNKNOWN"

def extract_date(text: str) -> str:
    """
    Find date by:
      - look for DATE_KEYS labels in lines
      - if found parse with normalize_date
      - fallback: scan first ~60 lines for any date pattern
    """
    if not text:
        return "UNKNOWN"
    t = normalize_text(text)
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    # label-based
    for ln in lines[:80]:
        low = ln.lower()
        if any(k in low for k in DATE_KEYS):
            # attempt to extract value after colon if present
            if ":" in ln:
                val = ln.split(":", 1)[1].strip()
                d = normalize_date(val)
                if d != "UNKNOWN":
                    return d
            # else try entire line
            d = normalize_date(ln)
            if d != "UNKNOWN":
                return d

    # fallback scan
    for ln in lines[:120]:
        d = normalize_date(ln)
        if d != "UNKNOWN":
            return d

    return "UNKNOWN"

def extract_amount(text: str) -> str:
    """
    Amount extraction strategy:
      1) Find lines with strong TOTAL keywords.
      2) From those lines pick the biggest money value in that context.
      3) If none, pick the maximum money candidate near bottom of doc.
    """
    if not text:
        return "UNKNOWN"

    t = normalize_text(text)
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    # 1) keyword lines
    best_val = None
    best_raw = None

    for ln in lines:
        low = ln.lower()

        if any(k in low for k in TOTAL_KEYS) and not any(b in low for b in BAD_TOTAL_CONTEXT if b not in {"total"}):
            cands = extract_money_candidates(ln)
            if cands:
                # prefer largest in this line
                val, raw, _ = max(cands, key=lambda x: x[0])
                if best_val is None or val > best_val:
                    best_val, best_raw = val, raw

    if best_raw:
        return best_raw

    # 2) fallback: consider bottom portion of doc (totals usually there)
    bottom = "\n".join(lines[-80:])
    cands = extract_money_candidates(bottom)
    if cands:
        val, raw, ctx = max(cands, key=lambda x: x[0])
        return raw

    return "UNKNOWN"

def extract_fields(text: str) -> dict:
    """
    Returns:
      vendor: string (raw)
      date:   YYYY_MM_DD or UNKNOWN
      amount: raw currency string or UNKNOWN
    """
    vendor = extract_vendor(text)
    date = extract_date(text)
    amount = extract_amount(text)
    return {"vendor": vendor, "date": date, "amount": amount}
