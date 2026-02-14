"""Tests for backend.logic.utils module."""
import pytest
from datetime import datetime
from backend.logic.utils import now_iso, make_id


class TestNowIso:
    """Test ISO timestamp generation."""

    def test_now_iso_format(self):
        """now_iso() returns ISO 8601 timestamp with Z suffix."""
        timestamp = now_iso()
        assert isinstance(timestamp, str)
        assert timestamp.endswith("Z")
        # Verify it's parseable as ISO datetime
        assert "T" in timestamp
        assert timestamp[:-1].count(":") >= 2

    def test_now_iso_recent(self):
        """now_iso() returns a recent timestamp (within last second)."""
        before = datetime.utcnow()
        timestamp = now_iso()
        after = datetime.utcnow()
        
        # Parse the ISO timestamp (remove Z suffix)
        ts_dt = datetime.fromisoformat(timestamp[:-1])
        
        assert before <= ts_dt <= after


class TestMakeId:
    """Test ID generation with prefixes."""

    def test_make_id_format(self):
        """make_id() returns prefix::uuid format."""
        id_val = make_id("user")
        assert "::" in id_val
        prefix, uuid_part = id_val.split("::")
        assert prefix == "user"
        # UUIDs are 36 chars with hyphens
        assert len(uuid_part) == 36

    def test_make_id_different_prefixes(self):
        """make_id() works with different prefixes."""
        prefixes = ["user", "upload", "analysis", "file", "ai"]
        for prefix in prefixes:
            id_val = make_id(prefix)
            assert id_val.startswith(f"{prefix}::")

    def test_make_id_uniqueness(self):
        """make_id() generates unique IDs."""
        ids = [make_id("test") for _ in range(100)]
        assert len(set(ids)) == 100, "Generated IDs should be unique"
