from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/oauth/callback")

TOKEN_FILE = "token.json"


def get_auth_url():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url


def save_token(code: str):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)

    creds = flow.credentials

    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


def get_drive_service():
    if not os.path.exists(TOKEN_FILE):
        raise Exception("Google Drive not connected yet")

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_to_drive(local_path, year, month, day):
    service = get_drive_service()

    # Create folders
    def get_or_create(name, parent=None):
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        if parent:
            q += f" and '{parent}' in parents"

        res = service.files().list(q=q, fields="files(id)").execute()
        files = res.get("files", [])
        if files:
            return files[0]["id"]

        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent:
            meta["parents"] = [parent]

        return service.files().create(body=meta, fields="id").execute()["id"]

    root = get_or_create("Invoices")
    year_f = get_or_create(year, root)
    month_f = get_or_create(month, year_f)
    day_f = get_or_create(day, month_f)

    file_metadata = {
        "name": os.path.basename(local_path),
        "parents": [day_f]
    }

    media = MediaFileUpload(local_path, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return uploaded["webViewLink"]
