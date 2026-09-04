"""Cau hinh tap trung, doc tu bien moi truong."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv

load_dotenv()

# Phase 1-2 chi doc. Muon agent gan label / archive thi doi sang
# "https://www.googleapis.com/auth/gmail.modify" VA xoa token.json de auth lai.
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Chan do dai body de khong dot token. Mot email marketing co the dai 50k ky tu.
MAX_BODY_CHARS = 4000

# Tran so email tra ve moi lan search, chan viec agent keo ca inbox vao context.
MAX_SEARCH_RESULTS = 25

Provider = Literal["openai", "openrouter", "google", "claude"]

DEFAULT_MODELS: dict[Provider, str] = {
    "openai": "gpt-4o-mini",
    "openrouter": "openai/gpt-4o-mini",
    "google": "gemini-2.0-flash",
    "claude": "claude-opus-5",
}

PROVIDER_API_KEYS: dict[Provider, str] = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "google": "GOOGLE_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}


@dataclass(frozen=True)
class ModelSettings:
    provider: Provider
    api_key: str
    model: str


@dataclass(frozen=True)
class GmailSettings:
    credentials_file: Path
    token_file: Path


def load_model_settings() -> ModelSettings:
    """Doc cau hinh LLM va kiem tra API key cua provider da chon."""
    raw_provider = os.getenv("EMAIL_AGENT_PROVIDER", "claude").strip().lower()
    if raw_provider not in DEFAULT_MODELS:
        supported = ", ".join(DEFAULT_MODELS)
        raise RuntimeError(
            f"EMAIL_AGENT_PROVIDER='{raw_provider}' khong hop le. "
            f"Cac gia tri ho tro: {supported}."
        )

    provider = cast(Provider, raw_provider)
    key_name = PROVIDER_API_KEYS[provider]
    api_key = os.getenv(key_name, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Thieu {key_name} cho provider '{provider}'. "
            "Copy .env.example thanh .env va dien key vao."
        )

    return ModelSettings(
        provider=provider,
        api_key=api_key,
        model=os.getenv("EMAIL_AGENT_MODEL", "").strip() or DEFAULT_MODELS[provider],
    )


def load_gmail_settings() -> GmailSettings:
    """Doc duong dan OAuth Gmail; khong phu thuoc provider hay API key LLM."""
    return GmailSettings(
        credentials_file=Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")),
        token_file=Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json")),
    )
