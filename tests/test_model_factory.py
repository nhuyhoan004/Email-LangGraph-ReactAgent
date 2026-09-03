"""Test factory LLM; chi khoi tao client, khong gui request API."""

from __future__ import annotations

from pathlib import Path

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from email_agent.agent.graph import build_model
from email_agent.config import DEFAULT_MODELS, Settings


def settings_for(provider: str) -> Settings:
    return Settings(
        provider=provider,  # type: ignore[arg-type]
        api_key="test-key",
        model=DEFAULT_MODELS[provider],  # type: ignore[index]
        credentials_file=Path("credentials.json"),
        token_file=Path("token.json"),
    )


@pytest.mark.parametrize(
    ("provider", "model_type"),
    [
        ("openai", ChatOpenAI),
        ("openrouter", ChatOpenAI),
        ("google", ChatGoogleGenerativeAI),
        ("claude", ChatAnthropic),
    ],
)
def test_build_model_uses_provider_adapter(provider, model_type):
    assert isinstance(build_model(settings_for(provider)), model_type)


def test_openrouter_uses_openrouter_endpoint():
    model = build_model(settings_for("openrouter"))

    assert str(model.openai_api_base).rstrip("/") == "https://openrouter.ai/api/v1"
