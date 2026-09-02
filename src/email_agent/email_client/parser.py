"""Parse payload MIME cua Gmail thanh text sach.

Day la phan ban nhat cua ca project: Gmail tra ve cay multipart long nhau,
body encode base64url, va rat nhieu email chi co ban HTML.
Tach rieng ra day de test duoc ma khong can goi API.
"""

from __future__ import annotations

import base64
import re
from html.parser import HTMLParser

_SKIP_TAGS = {"script", "style", "head", "title"}
_BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"}


class _TextExtractor(HTMLParser):
    """Bo tag HTML, giu lai text va xuong dong o cac the block."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag in _BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in _BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return normalize_whitespace(parser.get_text())


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def decode_b64url(data: str) -> str:
    """Gmail dung base64url va thuong thieu padding."""
    padded = data + "=" * (-len(data) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    return raw.decode("utf-8", errors="replace")


def get_header(payload: dict, name: str) -> str:
    """Header name khong phan biet hoa thuong theo RFC 5322."""
    target = name.lower()
    for header in payload.get("headers", []) or []:
        if header.get("name", "").lower() == target:
            return header.get("value", "")
    return ""


def _collect_parts(payload: dict, plain: list[str], html: list[str]) -> None:
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}) or {}
    data = body.get("data")

    if data:
        try:
            decoded = decode_b64url(data)
        except Exception:  # noqa: BLE001 - email loi encode khong duoc lam sap ca luong
            decoded = ""
        if mime == "text/plain":
            plain.append(decoded)
        elif mime == "text/html":
            html.append(decoded)

    for part in payload.get("parts", []) or []:
        _collect_parts(part, plain, html)


def extract_body(payload: dict, max_chars: int) -> tuple[str, bool]:
    """Tra ve (body, bi_cat_bot). Uu tien text/plain, fallback sang HTML."""
    plain: list[str] = []
    html: list[str] = []
    _collect_parts(payload, plain, html)

    if plain:
        text = normalize_whitespace("\n".join(plain))
    elif html:
        text = html_to_text("\n".join(html))
    else:
        text = ""

    if len(text) > max_chars:
        return text[:max_chars], True
    return text, False


def list_attachments(payload: dict) -> list[str]:
    """Ten cac file dinh kem. Chua tai ve, chi liet ke de agent biet co gi."""
    names: list[str] = []

    def walk(node: dict) -> None:
        filename = node.get("filename")
        if filename:
            names.append(filename)
        for part in node.get("parts", []) or []:
            walk(part)

    walk(payload)
    return names
