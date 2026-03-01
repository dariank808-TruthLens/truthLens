"""Tests for backend.logic.fallacy_detector."""
import pytest
from backend.logic.fallacy_detector import detect_fallacies


class TestDetectFallacies:
    def test_empty(self):
        assert detect_fallacies("") == []
        assert detect_fallacies("   ") == []

    def test_strawman(self):
        text = "They want to ban all books and destroy our freedom."
        fallacies = detect_fallacies(text)
        names = [f["name"] for f in fallacies]
        assert "Strawman" in names

    def test_bandwagon(self):
        text = "Everyone knows that this is the right approach. All real experts agree."
        fallacies = detect_fallacies(text)
        names = [f["name"] for f in fallacies]
        assert "Bandwagon" in names

    def test_structure(self):
        text = "They want to ban all books. Everyone agrees."
        fallacies = detect_fallacies(text)
        for f in fallacies:
            assert "id" in f
            assert "name" in f
            assert "statement" in f
            assert "severity" in f
            assert 0 <= f["severity"] <= 1
