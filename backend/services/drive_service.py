# backend/services/drive_service.py
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Config ---
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/

# Robust path checking for Deployment (Render) vs Local
def find_file(filename):
    # 1. Local Dev: backend/filename
    path1 = os.path.join(BASE_DIR, filename)
    if os.path.exists(path1): return path1
    
    # 2. Render Root: ./filename
    path2 = os.path.join(os.getcwd(), filename)
    if os.path.exists(path2): return path2
    
    # 3. Render Secrets: /etc/secrets/filename
    path3 = f"/etc/secrets/{filename}"
    if os.path.exists(path3): return path3
    
    return path1 # Default to backend/ for error msg

CREDENTIALS_FILE = find_file("credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json") # Token is always written to backend/ for now

# IMPT: On deploy, update Google Cloud Console "Authorized URIs" & set APP_BASE_URL env var.
REDIRECT_URI = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000") + "/oauth/callback"


def is_drive_connected() -> bool:
    """Frontend uses this via /drive/status."""
    return os.path.exists(TOKEN_FILE)



def _get_flow(code=None):
    # Case 1: Use File if exists
    if os.path.exists(CREDENTIALS_FILE):
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    # Case 2: Use Env Vars (Cloud Shell fallback)
    elif os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"):
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    else:
         raise Exception(f"Missing credentials! Please add 'backend/credentials.json' OR set GOOGLE_CLIENT_ID/SECRET env vars.")

    if code:
        flow.fetch_token(code=code)
    
    return flow

def get_auth_url() -> str:
    flow = _get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url


def save_token(code: str):
    flow = _get_flow(code=code)
    creds = flow.credentials
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())


def get_drive_service():
    if not is_drive_connected():
        raise Exception("Google Drive not connected. Please visit /connect-drive")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_to_drive(local_path, year, month, day):
    service = get_drive_service()

    root = get_or_create_folder(service, "Invoices")
    year_f = get_or_create_folder(service, year, root)
    month_f = get_or_create_folder(service, month, year_f)
    day_f = get_or_create_folder(service, day, month_f)

    file_metadata = {"name": os.path.basename(local_path), "parents": [day_f]}
    media = MediaFileUpload(local_path, resumable=True)

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,webViewLink",
    ).execute()

    folder_link = f"https://drive.google.com/drive/u/0/folders/{day_f}"

    return {
        "file_link": uploaded.get("webViewLink"),
        "folder_link": folder_link
    }


def disconnect_drive():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    return True

