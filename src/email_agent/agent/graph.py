"""Lap rap ReAct agent."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from ..config import Settings
from ..email_client.gmail import GmailClient
from .prompts import SYSTEM_PROMPT
from .tools import build_tools


def build_model(settings: Settings) -> ChatAnthropic:
    return ChatAnthropic(
        model=settings.model,
        api_key=settings.anthropic_api_key,
        max_tokens=16_000,
        # Adaptive thinking: model tu quyet dinh suy nghi bao lau. Tren Claude
        # 4.6 tro len khong dung budget_tokens nua.
        thinking={"type": "adaptive"},
    )


def build_agent(settings: Settings, client: GmailClient):
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
