
try:
    import pypdfium2 as pdfium
    print("pypdfium2 imported successfully")
except ImportError:
    print("pypdfium2 NOT installed")

from backend.services.ocr_service import ocr_pdf
print("Imported ocr_pdf function")
