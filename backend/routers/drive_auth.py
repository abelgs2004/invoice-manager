from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from backend.services.drive_service import get_auth_url, get_credentials, is_drive_connected

router = APIRouter()

@router.get("/drive/status")
def drive_status(request: Request):
    # Check session for credentials
    creds = request.session.get("user_creds")
    return JSONResponse({"connected": is_drive_connected(creds)})


@router.get("/connect-drive")
def connect_drive():
    return RedirectResponse(get_auth_url())


@router.get("/oauth/callback")
def oauth_callback(request: Request, code: str):
    # Exchange code for credentials and save to SESSION
    creds_json = get_credentials(code)
    request.session["user_creds"] = creds_json
    
    # send user back to your UI
    import os
    base_url = os.getenv("APP_BASE_URL")
    if not base_url and os.getenv("GOOGLE_REDIRECT_URI"):
        # Derive base URL from the redirect URI if possible
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        if "/oauth/callback" in redirect_uri:
            base_url = redirect_uri.replace("/oauth/callback", "")
    
    if not base_url:
        base_url = "http://127.0.0.1:8000"

    return RedirectResponse(url=f"{base_url}/")


@router.post("/disconnect-drive")
def disconnect_endpoint(request: Request):
    request.session.clear()
    return JSONResponse({"status": "disconnected"})

