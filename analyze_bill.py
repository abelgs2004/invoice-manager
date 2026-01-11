
import os
import sys
sys.path.append(os.getcwd())

from backend.services.pdf_service import extract_text_from_pdf
from backend.services.llm_service import extract_invoice_data_with_llm

FILENAME = "bill_2.pdf"

print(f"--- Analyzing {FILENAME} ---")

# 1. Get Text
try:
    text = extract_text_from_pdf(FILENAME)
    print(f"Extracted {len(text)} characters.")
    print("-" * 20)
    print(text)
    print("-" * 20)
    
    # 2. Test LLM directly
    print("\nTesting LLM Extraction...")
    data = extract_invoice_data_with_llm(text)
    print("LLM Result:", data)
    
except Exception as e:
    print(f"Error: {e}")
