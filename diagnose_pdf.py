
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

sys.path.append(os.getcwd())

from backend.services.pdf_service import extract_text_from_pdf
from backend.services.field_extractor import extract_fields
from backend.services.llm_service import extract_invoice_data_with_llm

FILENAME = "bill_2.pdf"

print(f"--- Diagnosing {FILENAME} ---")

if not os.path.exists(FILENAME):
    print("File not found!")
    sys.exit(1)

print("\n1. EXTRACTING TEXT...")
text = extract_text_from_pdf(FILENAME)
print(f"Text length: {len(text)}")
print("--- START TEXT ---")
print(text[:500]) # First 500 chars
print("--- END TEXT SAMPLE ---")

print("\n2. REGEX EXTRACTION...")
regex_res = extract_fields(text)
print("Regex Result:", regex_res)

print("\n3. LLM EXTRACTION...")
try:
    llm_res = extract_invoice_data_with_llm(text)
    print("LLM Result:", llm_res)
except Exception as e:
    print(f"LLM Failed: {e}")
