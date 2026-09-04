"""Test lua chon LLM provider ma khong goi API ben ngoai."""

from __future__ import annotations

import pytest

from email_agent.config import DEFAULT_MODELS, PROVIDER_API_KEYS, load_settings


@pytest.mark.parametrize("provider", list(DEFAULT_MODELS))
def test_load_settings_for_each_provider(monkeypatch, provider):
    for key_name in PROVIDER_API_KEYS.values():
        monkeypatch.delenv(key_name, raising=False)
    monkeypatch.setenv("EMAIL_AGENT_PROVIDER", provider)
    monkeypatch.setenv(PROVIDER_API_KEYS[provider], "test-key")
    monkeypatch.delenv("EMAIL_AGENT_MODEL", raising=False)

    settings = load_settings()

    assert settings.provider == provider
    assert settings.api_key == "test-key"
    assert settings.model == DEFAULT_MODELS[provider]


def test_load_settings_uses_custom_model(monkeypatch):
    monkeypatch.setenv("EMAIL_AGENT_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("EMAIL_AGENT_MODEL", "anthropic/claude-sonnet-4")

    assert load_settings().model == "anthropic/claude-sonnet-4"


def test_load_settings_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("EMAIL_AGENT_PROVIDER", "unknown")

    with pytest.raises(RuntimeError, match="khong hop le"):
        load_settings()


def test_load_settings_requires_selected_provider_key(monkeypatch):
    monkeypatch.setenv("EMAIL_AGENT_PROVIDER", "google")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        load_settings()
