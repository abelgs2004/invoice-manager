import os
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.ocr_service import extract_text_from_image

IMAGE_EXT = [".png", ".jpg", ".jpeg"]
PDF_EXT = [".pdf"]

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in PDF_EXT:
        text = extract_text_from_pdf(file_path)
        if text:
            return text

    if ext in IMAGE_EXT:
        return extract_text_from_image(file_path)

    return ""
