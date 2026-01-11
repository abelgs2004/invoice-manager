import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from backend/.env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from groq import Groq

# Configure
api_key = os.getenv("GROQ_API_KEY")

def extract_invoice_data_with_llm(ocr_text: str) -> dict:
    """
    Uses Groq (Llama 3) to extract structured data from raw OCR text.
    Returns None if extraction fails or API is not configured.
    """
    if not api_key:
        print("Groq API Key missing")
        return None

    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""
        Extract the following fields from the invoice/receipt text below:
        - vendor (store name)
        - date (format YYYY_MM_DD, use today's year if missing)
        - amount (the final total paid, validation: number with up to 2 decimal places, no currency symbols)

        Return ONLY a JSON object with keys: "vendor", "date", "amount".
        If a field is not found, use "UNKNOWN".

        Text:
        {ocr_text}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful data extraction assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        raw = completion.choices[0].message.content
        data = json.loads(raw)
        return data

    except Exception as e:
        print(f"LLM Extraction failed: {e}")
        # Propagate rate limit or connection errors
        raise e
