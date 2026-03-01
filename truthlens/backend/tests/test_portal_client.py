"""Tests for backend.logic.portal_client (HTTP client to the Couchbase portal)."""
import pytest
from unittest.mock import patch
import httpx

from backend.logic import portal_client
from backend.logic.portal_client import PortalError


def _make_response(status_code: int, json_body=None, text: str = ""):
    """Build an httpx.Response-like object with fixed status_code and json()."""
    resp = httpx.Response(status_code=status_code, text=text or "{}")
    if json_body is not None:
        resp.json = lambda: json_body
    return resp


class TestCheckHealth:
    """Test portal health check."""

    def test_health_ok(self):
        """check_health returns (True, 'ok') when portal returns 200 and db connected."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(
                200, {"status": "ok", "db": "connected"}
            )

            ok, msg = portal_client.check_health()
            assert ok is True
            assert msg == "ok"

    def test_health_unreachable(self):
        """check_health returns (False, msg) when request fails."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.get.side_effect = httpx.ConnectError("connection refused")

            ok, msg = portal_client.check_health()
            assert ok is False
            assert "unreachable" in msg or "refused" in msg

    def test_health_bad_status(self):
        """check_health returns False when portal returns non-200."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(503, None, "unavailable")

            ok, msg = portal_client.check_health()
            assert ok is False
            assert "503" in msg


class TestSaveDocument:
    """Test save_document."""

    def test_save_success(self):
        """save_document succeeds on 200 response."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.post.return_value = _make_response(200)

            portal_client.save_document("doc1", {"key": "value"})
            mock_http.post.assert_called_once()
            call_kw = mock_http.post.call_args[1]
            assert call_kw["json"] == {"id": "doc1", "data": {"key": "value"}}

    def test_save_500_raises(self):
        """save_document raises PortalError on 500."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.post.return_value = _make_response(500, None, "internal error")

            with pytest.raises(PortalError) as exc_info:
                portal_client.save_document("doc1", {})
            assert "500" in str(exc_info.value)


class TestGetDocument:
    """Test get_document."""

    def test_get_success(self):
        """get_document returns parsed JSON on 200."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(
                200, {"id": "doc1", "name": "test"}
            )

            result = portal_client.get_document("doc1")
            assert result == {"id": "doc1", "name": "test"}

    def test_get_404_returns_none(self):
        """get_document returns None on 404."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(404)

            result = portal_client.get_document("missing")
            assert result is None


class TestDeleteDocument:
    """Test delete_document."""

    def test_delete_success(self):
        """delete_document returns True on 200."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.delete.return_value = _make_response(200)

            assert portal_client.delete_document("doc1") is True

    def test_delete_404_returns_false(self):
        """delete_document returns False on 404."""
        with patch.object(portal_client, "_client") as mock_client_factory:
            mock_http = mock_client_factory.return_value.__enter__.return_value
            mock_http.delete.return_value = _make_response(404)

            assert portal_client.delete_document("missing") is False
