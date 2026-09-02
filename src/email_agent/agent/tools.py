"""Boc GmailClient thanh LangChain tools.

Docstring cua moi ham chinh la mo ta ma model doc de quyet dinh goi tool nao,
nen viet cho ro rang.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, tool

from ..email_client.gmail import GmailClient


def _wrap_untrusted(text: str) -> str:
    """Danh dau ro noi dung do nguoi ngoai viet, khop voi luat trong system prompt."""
    return f"<email_content>\n{text}\n</email_content>"


def build_tools(client: GmailClient) -> list[BaseTool]:
    @tool
    def search_emails(query: str, max_results: int = 10) -> str:
        """Tim email trong hop thu bang cu phap query cua Gmail.

        Tra ve metadata (nguoi gui, tieu de, ngay, snippet) chu khong tra ve
        toan bo noi dung. Dung get_email voi id de doc chi tiet.

        Args:
            query: Query Gmail, vi du "is:unread newer_than:3d category:primary".
                Chuoi rong nghia la lay email moi nhat trong hop thu.
            max_results: So email toi da, toi da 25.
        """
        results = client.search(query, max_results)
        if not results:
            return f"Khong tim thay email nao khop voi query: {query!r}"
        header = f"Tim thay {len(results)} email cho query {query!r}:\n\n"
        return header + _wrap_untrusted(
            "\n\n".join(item.to_text() for item in results)
        )

    @tool
    def get_email(message_id: str) -> str:
        """Doc toan bo noi dung mot email theo id.

        Body dai se bi cat bot de tiet kiem token. Lay message_id tu ket qua
        cua search_emails.
        """
        return _wrap_untrusted(client.get_email(message_id).to_text())

    @tool
    def get_thread(thread_id: str) -> str:
        """Doc ca luong hoi thoai theo thu tu thoi gian.

        Dung khi can hieu ngu canh qua lai giua nhieu email, vi du truoc khi
        soan cau tra loi. Lay thread_id tu ket qua cua search_emails.
        """
        emails = client.get_thread(thread_id)
        if not emails:
            return f"Khong tim thay luong hoi thoai {thread_id!r}"
        body = "\n\n---\n\n".join(email.to_text() for email in emails)
        return f"Luong co {len(emails)} email:\n\n" + _wrap_untrusted(body)

    @tool
    def list_labels() -> str:
        """Liet ke tat ca label dang co trong hop thu.

        Huu ich khi nguoi dung nhac den mot label ma ban chua biet ten chinh xac.
        """
        labels = client.list_labels()
        return "Cac label hien co:\n" + "\n".join(f"- {name}" for name in labels)

    return [search_emails, get_email, get_thread, list_labels]
