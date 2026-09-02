"""Verify Phase 1: doc duoc Gmail chua, hoan toan khong dung AI.

Chay cai nay TRUOC khi dung agent. Neu no chay duoc thi phan OAuth va parser
da on, moi loi con lai la o phia agent.

    python scripts/check_inbox.py
    python scripts/check_inbox.py "is:unread newer_than:7d"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from email_agent.config import load_settings  # noqa: E402
from email_agent.email_client.gmail import GmailClient  # noqa: E402


def main() -> int:
    query = sys.argv[1] if len(sys.argv) > 1 else "in:inbox"
    settings = load_settings()
    client = GmailClient(settings.credentials_file, settings.token_file)

    print(f"Hop thu: {client.profile_email()}")
    print(f"Query:   {query!r}\n")

    results = client.search(query, max_results=10)
    if not results:
        print("Khong co email nao khop.")
        return 0

    for i, item in enumerate(results, 1):
        print(f"{i}. [{item.date}] {item.sender}")
        print(f"   {item.subject}")
        print(f"   {item.snippet[:120]}\n")

    first = client.get_email(results[0].id)
    print("--- Body cua email dau tien (kiem tra parser) ---")
    print(first.body[:600] or "(rong)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
