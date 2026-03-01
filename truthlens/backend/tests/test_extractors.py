"""Tests for backend.logic.extractors."""
import pytest
from backend.logic.extractors import extract_text


class TestExtractText:
    def test_txt(self):
        out = extract_text("doc.txt", b"Hello world\nLine two")
        assert "Hello world" in out
        assert "Line two" in out

    def test_md(self):
        out = extract_text("readme.md", b"# Title\n\nSome **bold** text")
        assert "Title" in out
        assert "bold" in out

    def test_empty(self):
        assert extract_text("x.txt", b"") == ""
        assert extract_text("x.txt", b"   \n  ") == ""

    def test_unsupported_fallback(self):
        # Unknown extension tries UTF-8 decode
        out = extract_text("data.xyz", b"plain text here")
        assert "plain text" in out or out == ""
