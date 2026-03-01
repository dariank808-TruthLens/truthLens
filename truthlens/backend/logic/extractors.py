"""Extract plain text from various file types for analysis.

Supports: .txt, .md, .pdf, .docx, .html
Used for logical fallacy and fact-check pipelines. Video support later
via speech-to-text, then reuse this pipeline on the transcript.
"""
from __future__ import annotations

from typing import Optional

# Lazy imports to avoid loading heavy libs when not needed


def extract_text(filename: str, content: bytes, content_type: Optional[str] = None) -> str:
    """Extract plain text from file content.

    Args:
        filename: Original filename (used for extension detection)
        content: Raw file bytes
        content_type: Optional MIME type (e.g. application/pdf)

    Returns:
        Extracted plain text, or empty string if unsupported/error
    """
    ext = (filename.rsplit(".", 1)[-1].lower() if "." in filename else "") or ""
    ext = ext or _mime_to_ext(content_type or "")

    if ext in ("txt", "text", "md", "markdown"):
        return content.decode("utf-8", errors="replace").strip()

    if ext == "pdf":
        return _extract_pdf(content)

    if ext in ("docx", "doc"):
        return _extract_docx(content)

    if ext in ("html", "htm"):
        return _extract_html(content)

    # Fallback: try UTF-8 decode for unknown text-like formats
    try:
        return content.decode("utf-8", errors="replace").strip()
    except Exception:
        return ""


def _mime_to_ext(mime: str) -> str:
    m = mime.lower()
    if "pdf" in m:
        return "pdf"
    if "word" in m or "docx" in m or "msword" in m:
        return "docx"
    if "html" in m:
        return "html"
    if "markdown" in m or "md" in m:
        return "md"
    if "plain" in m or "text" in m:
        return "txt"
    return ""


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(content))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n\n".join(parts).strip()
    except Exception:
        return ""


def _extract_docx(content: bytes) -> str:
    try:
        from docx import Document
        from io import BytesIO
        doc = Document(BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    except Exception:
        return ""


def _extract_html(content: bytes) -> str:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception:
        return content.decode("utf-8", errors="replace").strip()
