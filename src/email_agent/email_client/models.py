"""Kieu du lieu thuan, khong phu thuoc Gmail API hay LangChain."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmailSummary:
    """Metadata nhe, dung cho ket qua search. Khong chua body."""

    id: str
    thread_id: str
    sender: str
    subject: str
    date: str
    snippet: str
    labels: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        labels = ", ".join(self.labels) if self.labels else "-"
        return (
            f"id: {self.id}\n"
            f"thread_id: {self.thread_id}\n"
            f"from: {self.sender}\n"
            f"subject: {self.subject}\n"
            f"date: {self.date}\n"
            f"labels: {labels}\n"
            f"snippet: {self.snippet}"
        )


@dataclass
class Email(EmailSummary):
    """Email day du, co body da parse."""

    to: str = ""
    cc: str = ""
    body: str = ""
    body_truncated: bool = False

    def to_text(self) -> str:
        note = "\n[body da bi cat bot vi qua dai]" if self.body_truncated else ""
        return (
            f"id: {self.id}\n"
            f"thread_id: {self.thread_id}\n"
            f"from: {self.sender}\n"
            f"to: {self.to}\n"
            f"cc: {self.cc or '-'}\n"
            f"subject: {self.subject}\n"
            f"date: {self.date}\n"
            f"labels: {', '.join(self.labels) if self.labels else '-'}\n"
            f"---\n{self.body}{note}"
        )
