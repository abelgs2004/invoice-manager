# backend/routers/drive_auth.py
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from backend.services.drive_service import get_auth_url, save_token, is_drive_connected, disconnect_drive

router = APIRouter()

@router.get("/drive/status")
def drive_status():
    # frontend calls this to know if Drive is connected
    return JSONResponse({"connected": is_drive_connected()})


@router.get("/connect-drive")
def connect_drive():
    return RedirectResponse(get_auth_url())


@router.get("/oauth/callback")
def oauth_callback(code: str):
    save_token(code)
    # send user back to your UI
    import os
    base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
    return RedirectResponse(url=f"{base_url}/")


@router.post("/disconnect-drive")
def disconnect_endpoint():
    disconnect_drive()
    return JSONResponse({"status": "disconnected"})

