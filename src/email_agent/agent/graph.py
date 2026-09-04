"""Lap rap ReAct agent."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from ..config import ModelSettings
from ..email_client.gmail import GmailClient
from .prompts import SYSTEM_PROMPT
from .tools import build_tools


def build_model(settings: ModelSettings) -> BaseChatModel:
    """Khoi tao chat model tu provider da chon trong .env."""
    if settings.provider == "claude":
        return ChatAnthropic(
            model=settings.model,
            api_key=settings.api_key,
            max_tokens=16_000,
            # Adaptive thinking chi la tham so cua Claude.
            thinking={"type": "adaptive"},
        )

    if settings.provider == "google":
        return ChatGoogleGenerativeAI(
            model=settings.model,
            google_api_key=settings.api_key,
            max_output_tokens=16_000,
        )

    if settings.provider == "openrouter":
        return ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=16_000,
        )

    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        max_tokens=16_000,
    )


def build_agent(settings: ModelSettings, client: GmailClient):
    """Tra ve (graph da compile, dia chi email cua user)."""
    user_email = client.profile_email()
    return (
        create_react_agent(
            model=build_model(settings),
            tools=build_tools(client),
            prompt=SYSTEM_PROMPT.format(user_email=user_email),
            # MemorySaver giu lich su trong RAM. Sang Phase 4 doi sang
            # SqliteSaver de state song qua cac lan chay.
            checkpointer=MemorySaver(),
        ),
        user_email,
    )
