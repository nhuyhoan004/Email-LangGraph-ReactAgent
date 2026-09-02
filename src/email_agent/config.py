"""Cau hinh tap trung, doc tu bien moi truong."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Phase 1-2 chi doc. Muon agent gan label / archive thi doi sang
# "https://www.googleapis.com/auth/gmail.modify" VA xoa token.json de auth lai.
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Chan do dai body de khong dot token. Mot email marketing co the dai 50k ky tu.
MAX_BODY_CHARS = 4000

# Tran so email tra ve moi lan search, chan viec agent keo ca inbox vao context.
MAX_SEARCH_RESULTS = 25


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    model: str
    credentials_file: Path
    token_file: Path


def load_settings() -> Settings:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "Thieu ANTHROPIC_API_KEY. Copy .env.example thanh .env va dien key vao."
        )
    return Settings(
        anthropic_api_key=api_key,
        model=os.getenv("EMAIL_AGENT_MODEL", "claude-opus-5"),
        credentials_file=Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")),
        token_file=Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json")),
    )
