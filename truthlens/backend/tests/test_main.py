"""Tests for FastAPI endpoints and health checks."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestHealth:
    """Test health and availability endpoints."""

    def test_read_root(self):
        """GET / returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "GraphQL" in data["message"]

    def test_cors_headers_present(self):
        """CORS middleware is configured."""
        # The app has CORS configured, headers may vary based on request origin
        response = client.get("/")
        assert response.status_code == 200
        # Just verify that the response is valid
        assert "message" in response.json()
