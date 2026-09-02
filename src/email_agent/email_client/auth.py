"""OAuth flow cho Gmail. Chay mot lan roi cache vao token.json."""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..config import GMAIL_SCOPES


def get_credentials(credentials_file: Path, token_file: Path) -> Credentials:
    creds: Credentials | None = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), GMAIL_SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"Khong tim thay {credentials_file}.\n"
                "Vao Google Cloud Console > APIs & Services > Credentials, tao OAuth "
                "client ID kieu 'Desktop app', tai file JSON ve va doi ten thanh "
                f"{credentials_file}."
            )
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), GMAIL_SCOPES
        )
        creds = flow.run_local_server(port=0)

    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds
