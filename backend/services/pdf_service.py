from backend.utils.text_utils import normalize_text
from backend.services.ocr_service import ocr_pdf


def extract_text_from_pdf(pdf_path: str) -> str:
    text_parts = []

    # 1) pdfplumber first (best for structured PDFs)
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                if t.strip():
                    text_parts.append(t)
        joined = "\n\n".join(text_parts).strip()
        if len(joined) > 30:
            return normalize_text(joined)
    except Exception:
        pass

    # 2) pypdf fallback
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for p in reader.pages:
            t = p.extract_text() or ""
            if t.strip():
                text_parts.append(t)
        
        candidate = normalize_text("\n\n".join(text_parts).strip())
        # If we found substantial text, return it. Otherwise fall through.
        if len(candidate) > 20:
            return candidate
    except Exception:
        pass
        
    # 3) Fallback to OCR for scanned PDFs
    return ocr_pdf(pdf_path)

