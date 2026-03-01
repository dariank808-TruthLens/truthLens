"""HTTP client for the TypeScript Couchbase portal.

This module is the ONLY place in the Python backend that knows how to talk
to the Couchbase portal. The rest of the backend should go through
`backend.logic.store` for persistence.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx


def _env_flag(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default)
    return value.lower() in {"1", "true", "yes", "on"}


# Whether the Python backend should use the portal for persistence.
# Defaults to False so tests and local runs can use in-memory storage
# unless explicitly enabled.
USE_PORTAL: bool = _env_flag("USE_PORTAL", "false")

# Base URL for the TypeScript Couchbase portal (without trailing slash).
# Example: http://localhost:3000/api
PORTAL_BASE_URL: str = os.getenv("COUCHBASE_PORTAL_URL", "http://localhost:3000/api")

# Default network timeout in seconds for portal calls.
DEFAULT_TIMEOUT: float = float(os.getenv("PORTAL_TIMEOUT_SECONDS", "5.0"))


class PortalError(RuntimeError):
    """Generic error when talking to the portal."""


def is_enabled() -> bool:
    """Return True if the portal should be used for persistence."""
    # Re-evaluate in case the environment was changed after import.
    return _env_flag("USE_PORTAL", "false")


def _client() -> httpx.Client:
    """Create a configured HTTPX client for talking to the portal."""
    return httpx.Client(timeout=DEFAULT_TIMEOUT)


def save_document(doc_id: str, data: Dict[str, Any]) -> None:
    """Save a document via the portal.

    The TypeScript portal exposes POST /api/save with JSON body:
        { "id": <doc_id>, "data": <arbitrary JSON> }
    """
    url = f"{PORTAL_BASE_URL}/save"
    payload = {"id": doc_id, "data": data}

    try:
        with _client() as client:
            response = client.post(url, json=payload)
    except httpx.RequestError as exc:
        raise PortalError(f"Failed to reach portal at {url}: {exc!r}") from exc

    if response.status_code >= 500:
        raise PortalError(
            f"Portal server error on save_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )

    if response.status_code >= 400:
        raise PortalError(
            f"Portal rejected save_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a document via the portal.

    The TypeScript portal exposes GET /api/get/:id and returns the JSON
    document content on success, or 404 if not found.
    """
    url = f"{PORTAL_BASE_URL}/get/{doc_id}"

    try:
        with _client() as client:
            response = client.get(url)
    except httpx.RequestError as exc:
        raise PortalError(f"Failed to reach portal at {url}: {exc!r}") from exc

    if response.status_code == 404:
        return None

    if response.status_code >= 500:
        raise PortalError(
            f"Portal server error on get_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )

    if response.status_code >= 400:
        raise PortalError(
            f"Portal rejected get_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise PortalError(
            f"Portal returned invalid JSON for get_document({doc_id!r}): "
            f"body={response.text!r}"
        ) from exc


def delete_document(doc_id: str) -> bool:
    """Delete a document via the portal.

    The TypeScript portal exposes DELETE /api/delete/:id and returns:
      - 200 JSON {\"success\": true} on successful delete
      - 404 JSON {\"error\": \"not found\"} if the document does not exist
    """
    url = f"{PORTAL_BASE_URL}/delete/{doc_id}"

    try:
        with _client() as client:
            response = client.delete(url)
    except httpx.RequestError as exc:
        raise PortalError(f"Failed to reach portal at {url}: {exc!r}") from exc

    if response.status_code == 404:
        return False

    if response.status_code >= 500:
        raise PortalError(
            f"Portal server error on delete_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )

    if response.status_code >= 400:
        raise PortalError(
            f"Portal rejected delete_document({doc_id!r}): "
            f"status={response.status_code}, body={response.text!r}"
        )

    return True


def check_health() -> tuple[bool, str]:
    """Check if the portal is reachable and healthy.

    Returns (ok, message). ok is True if GET /api/health returns 200
    with status "ok"; otherwise False with a short message.
    """
    url = f"{PORTAL_BASE_URL}/health"
    try:
        with _client() as client:
            response = client.get(url)
    except httpx.RequestError as exc:
        return False, f"portal unreachable: {exc!r}"
    if response.status_code != 200:
        return False, f"portal returned {response.status_code}"
    try:
        data = response.json()
        if data.get("status") == "ok" and data.get("db") == "connected":
            return True, "ok"
        return False, data.get("db", "unknown")
    except ValueError:
        return False, "invalid health response"
