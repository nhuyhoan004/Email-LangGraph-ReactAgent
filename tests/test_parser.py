"""Test parser MIME - chay duoc ma khong can Gmail credentials."""

from __future__ import annotations

import base64

from email_agent.email_client.parser import (
    extract_body,
    get_header,
    html_to_text,
    list_attachments,
)


def b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def test_get_header_is_case_insensitive():
    payload = {"headers": [{"name": "From", "value": "a@b.com"}]}
    assert get_header(payload, "from") == "a@b.com"
    assert get_header(payload, "Missing") == ""


def test_extract_body_prefers_plain_text():
    payload = {
        "mimeType": "multipart/alternative",
        "parts": [
            {"mimeType": "text/plain", "body": {"data": b64("noi dung thuan")}},
            {"mimeType": "text/html", "body": {"data": b64("<p>ban html</p>")}},
        ],
    }
    body, truncated = extract_body(payload, 1000)
    assert body == "noi dung thuan"
    assert truncated is False


def test_extract_body_falls_back_to_html():
    payload = {
        "mimeType": "text/html",
        "body": {"data": b64("<div>Xin chao<br>the gioi</div>")},
    }
    body, _ = extract_body(payload, 1000)
    assert "Xin chao" in body
    assert "the gioi" in body
    assert "<div>" not in body


def test_extract_body_handles_nested_multipart():
    payload = {
        "mimeType": "multipart/mixed",
        "parts": [
            {
                "mimeType": "multipart/alternative",
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": b64("sau ba lop")}}
                ],
            }
        ],
    }
    body, _ = extract_body(payload, 1000)
    assert body == "sau ba lop"


def test_extract_body_truncates():
    payload = {"mimeType": "text/plain", "body": {"data": b64("x" * 500)}}
    body, truncated = extract_body(payload, 100)
    assert len(body) == 100
    assert truncated is True


def test_html_to_text_drops_script_and_style():
    html = "<style>p{color:red}</style><p>giu lai</p><script>alert(1)</script>"
    text = html_to_text(html)
    assert text == "giu lai"


def test_list_attachments():
    payload = {
        "parts": [
            {"filename": "", "mimeType": "text/plain"},
            {"filename": "hopdong.pdf", "mimeType": "application/pdf"},
        ]
    }
    assert list_attachments(payload) == ["hopdong.pdf"]
