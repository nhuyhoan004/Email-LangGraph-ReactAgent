"""Chat CLI. Diem vao chinh cua Phase 2."""

from __future__ import annotations

import sys
import uuid

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent.graph import build_agent
from .config import load_settings
from .email_client.gmail import GmailClient

console = Console()


def _text_of(message: object) -> str:
    """Lay phan text tu AIMessage. Khi bat thinking, content la list block."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts).strip()


def _run_turn(agent, question: str, config: dict) -> None:
    for chunk in agent.stream(
        {"messages": [("user", question)]}, config, stream_mode="updates"
    ):
        for node, update in chunk.items():
            for message in update.get("messages", []) or []:
                # Hien thi tool call de biet agent dang lam gi, thay vi treo im lang.
                for call in getattr(message, "tool_calls", None) or []:
                    console.print(
                        f"  [dim]-> {call['name']}({call.get('args', {})})[/dim]"
                    )
                if node == "agent":
                    text = _text_of(message)
                    if text:
                        console.print()
                        console.print(Markdown(text))


def main() -> int:
    try:
        settings = load_settings()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1

    console.print("[dim]Dang ket noi Gmail...[/dim]")
    try:
        client = GmailClient(settings.credentials_file, settings.token_file)
        agent, user_email = build_agent(settings, client)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1

    console.print(
        Panel(
            f"Hop thu: [bold]{user_email}[/bold]\n"
            f"Model: [bold]{settings.model}[/bold]\n"
            "Che do: [bold]chi doc[/bold] - agent khong the sua hop thu\n\n"
            "Thu hoi: 'hom nay co mail nao can tra loi gap khong?'\n"
            "Go 'thoat' de ket thuc.",
            title="Email Agent",
        )
    )

    # Cung mot thread_id qua ca phien -> agent nho cac luot truoc.
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    while True:
        try:
            question = console.input("\n[bold cyan]Ban:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Tam biet.[/dim]")
            return 0

        if not question:
            continue
        if question.lower() in {"thoat", "exit", "quit", "q"}:
            console.print("[dim]Tam biet.[/dim]")
            return 0

        try:
            _run_turn(agent, question, config)
        except Exception as exc:  # noqa: BLE001 - loi mot luot khong nen giet CLI
            console.print(f"[red]Loi: {exc}[/red]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
