import pytesseract
from PIL import Image
from pdf2image import convert_from_path

import os

# Configurable path via env, or default/system path
tess_env = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(tess_env):
    pytesseract.pytesseract.tesseract_cmd = tess_env
# On Linux/Cloud, if "tesseract" is in PATH, we might not need to set this at all, 
# or we set TESSERACT_CMD=/usr/bin/tesseract


def ocr_image(image_path: str) -> str:
    img = Image.open(image_path)

    text = pytesseract.image_to_string(
        img,
        lang="eng",
        config="--oem 3 --psm 6"
    )
    return text


import pypdfium2 as pdfium

def ocr_pdf(pdf_path: str) -> str:
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        full_text = []
        for i in range(len(pdf)):
            page = pdf[i]
            # Render to image (scale=3 is roughly 200-300dpi, good for OCR)
            bitmap = page.render(scale=3)
            pil_image = bitmap.to_pil()
            
            text = pytesseract.image_to_string(
                pil_image,
                lang="eng",
                config="--oem 3 --psm 6"
            )
            full_text.append(text)
        
        pdf.close() # Explicit close
        return "\n".join(full_text)
    except Exception as e:
        print(f"OCR PDF failed: {e}")
        return ""
