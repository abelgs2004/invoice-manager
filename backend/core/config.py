# backend/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/oauth/callback")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

STORAGE_ROOT = os.getenv("STORAGE_ROOT", "storage")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")

# For CORS
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
