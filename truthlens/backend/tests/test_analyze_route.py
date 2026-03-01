"""Tests for /api/analyze upload endpoint."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_analyze_no_files():
    resp = client.post("/api/analyze", data={"fact_check": "true", "logical_fallacy_check": "true"})
    assert resp.status_code == 422  # missing required files


def test_analyze_txt_file():
    content = b"They want to ban all books. Everyone knows this is true."
    files = [("files", ("test.txt", content, "text/plain"))]
    data = {"fact_check": "true", "logical_fallacy_check": "true", "ai_generation_check": "false"}
    resp = client.post("/api/analyze", files=files, data=data)
    assert resp.status_code == 200
    j = resp.json()
    assert "breakdown" in j
    assert "fallacies" in j
    assert "fact_checks" in j
    assert "files" in j
    # Should detect at least one fallacy (Strawman, Bandwagon)
    assert len(j["fallacies"]) >= 1
    assert j["breakdown"].get("overall_credibility_score") is not None
