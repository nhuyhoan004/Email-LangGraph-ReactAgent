"""Adapter Gmail. Thuan Python, khong biet gi ve LLM.

Chay duoc doc lap qua scripts/check_inbox.py de verify truoc khi dung agent.
"""

from __future__ import annotations

from pathlib import Path

from googleapiclient.discovery import build

from ..config import MAX_BODY_CHARS, MAX_SEARCH_RESULTS
from .auth import get_credentials
from .models import Email, EmailSummary
from .parser import extract_body, get_header, list_attachments

# Label he thong cua Gmail hien thi kho doc, doi sang ten than thien hon.
_LABEL_ALIASES = {
    "INBOX": "Inbox",
    "UNREAD": "Chua doc",
    "STARRED": "Da gan sao",
    "IMPORTANT": "Quan trong",
    "SENT": "Da gui",
    "DRAFT": "Nhap",
    "SPAM": "Spam",
    "TRASH": "Thung rac",
    "CATEGORY_PERSONAL": "Ca nhan",
    "CATEGORY_SOCIAL": "Mang xa hoi",
    "CATEGORY_PROMOTIONS": "Quang cao",
    "CATEGORY_UPDATES": "Cap nhat",
    "CATEGORY_FORUMS": "Dien dan",
}


def _pretty_labels(label_ids: list[str]) -> list[str]:
    return [_LABEL_ALIASES.get(lid, lid) for lid in label_ids]


class GmailClient:
    def __init__(self, credentials_file: Path, token_file: Path) -> None:
        creds = get_credentials(credentials_file, token_file)
        self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    def search(self, query: str, max_results: int = 10) -> list[EmailSummary]:
        """query dung cu phap Gmail: 'is:unread from:sep@x.com newer_than:7d'."""
        capped = max(1, min(max_results, MAX_SEARCH_RESULTS))
        listing = (
            self._service.users()
            .messages()
            .list(userId="me", q=query, maxResults=capped)
            .execute()
        )

        results: list[EmailSummary] = []
        for ref in listing.get("messages", []) or []:
            # format=metadata: chi lay header, khong keo body ve -> nhanh va re.
            msg = (
                self._service.users()
                .messages()
                .get(
                    userId="me",
                    id=ref["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            payload = msg.get("payload", {}) or {}
            results.append(
                EmailSummary(
                    id=msg["id"],
                    thread_id=msg.get("threadId", ""),
                    sender=get_header(payload, "From"),
                    subject=get_header(payload, "Subject") or "(khong co tieu de)",
                    date=get_header(payload, "Date"),
                    snippet=msg.get("snippet", ""),
                    labels=_pretty_labels(msg.get("labelIds", []) or []),
                )
            )
        return results

    def get_email(self, message_id: str) -> Email:
        msg = (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        payload = msg.get("payload", {}) or {}
        body, truncated = extract_body(payload, MAX_BODY_CHARS)
        attachments = list_attachments(payload)
        if attachments:
            body += "\n\n[File dinh kem: " + ", ".join(attachments) + "]"

        return Email(
            id=msg["id"],
            thread_id=msg.get("threadId", ""),
            sender=get_header(payload, "From"),
            to=get_header(payload, "To"),
            cc=get_header(payload, "Cc"),
            subject=get_header(payload, "Subject") or "(khong co tieu de)",
            date=get_header(payload, "Date"),
            snippet=msg.get("snippet", ""),
            labels=_pretty_labels(msg.get("labelIds", []) or []),
            body=body,
            body_truncated=truncated,
        )

    def get_thread(self, thread_id: str) -> list[Email]:
        thread = (
            self._service.users()
            .threads()
            .get(userId="me", id=thread_id, format="full")
            .execute()
        )
        emails: list[Email] = []
        for msg in thread.get("messages", []) or []:
            payload = msg.get("payload", {}) or {}
            body, truncated = extract_body(payload, MAX_BODY_CHARS)
            emails.append(
                Email(
                    id=msg["id"],
                    thread_id=msg.get("threadId", ""),
                    sender=get_header(payload, "From"),
                    to=get_header(payload, "To"),
                    cc=get_header(payload, "Cc"),
                    subject=get_header(payload, "Subject") or "(khong co tieu de)",
                    date=get_header(payload, "Date"),
                    snippet=msg.get("snippet", ""),
                    labels=_pretty_labels(msg.get("labelIds", []) or []),
                    body=body,
                    body_truncated=truncated,
                )
            )
        return emails

    def list_labels(self) -> list[str]:
        resp = self._service.users().labels().list(userId="me").execute()
        return sorted(label["name"] for label in resp.get("labels", []) or [])

    def profile_email(self) -> str:
        return self._service.users().getProfile(userId="me").execute().get(
            "emailAddress", ""
        )
