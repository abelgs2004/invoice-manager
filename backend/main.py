# backend/main.py
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Routers
from backend.routers.upload import router as upload_router
from backend.routers.drive_auth import router as drive_router
from backend.logging_setup import setup_logging

from starlette.middleware.sessions import SessionMiddleware

setup_logging()
app = FastAPI(title="Invoice Processing API", version="1.0.0")

# Add Session Middleware (Keys should be in .env for production)
# This encrypts the session data (like google tokens) in a cookie
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "super-secret-key-change-me"),
    session_cookie="invoice_session",
    max_age=86400 * 7, # 7 days
    https_only=False # Set to True in production with SSL
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drive_router)
app.include_router(upload_router)

# Serve frontend at root (must be last)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
