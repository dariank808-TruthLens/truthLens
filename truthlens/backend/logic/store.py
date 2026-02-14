"""Data store abstraction for users, uploads, and analyses.

Supports both in-memory (fallback) and Couchbase backends.
Uses Couchbase when available, falls back to in-memory for testing.
"""
from typing import Optional, Dict, Any

from .couchbase_config import CouchbaseConfig
from .couchbase_client import CouchbaseQuery, CouchbaseClient

# In-memory fallback store (used when Couchbase is disabled)
_users: Dict[str, Dict[str, Any]] = {}
_uploads: Dict[str, Dict[str, Any]] = {}
_analyses: Dict[str, Dict[str, Any]] = {}


def _use_couchbase() -> bool:
    """Check if Couchbase should be used."""
    return CouchbaseConfig.USE_COUCHBASE and CouchbaseClient.is_connected()


# --- User Store ---

def save_user(user_id: str, user_doc: Dict[str, Any]) -> None:
    """Save a user document."""
    if _use_couchbase():
        CouchbaseQuery.save_document(user_id, user_doc)
    else:
        _users[user_id] = user_doc


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.get_document(user_id)
    else:
        return _users.get(user_id)


def delete_user(user_id: str) -> bool:
    """Delete a user document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.delete_document(user_id)
    else:
        if user_id in _users:
            del _users[user_id]
            return True
        return False


# --- Upload Store ---

def save_upload(upload_id: str, upload_doc: Dict[str, Any]) -> None:
    """Save an upload document."""
    if _use_couchbase():
        CouchbaseQuery.save_document(upload_id, upload_doc)
    else:
        _uploads[upload_id] = upload_doc


def get_upload(upload_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an upload document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.get_document(upload_id)
    else:
        return _uploads.get(upload_id)


def delete_upload(upload_id: str) -> bool:
    """Delete an upload document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.delete_document(upload_id)
    else:
        if upload_id in _uploads:
            del _uploads[upload_id]
            return True
        return False


# --- Analysis Store ---

def save_analysis(analysis_id: str, analysis_doc: Dict[str, Any]) -> None:
    """Save an analysis document."""
    if _use_couchbase():
        CouchbaseQuery.save_document(analysis_id, analysis_doc)
    else:
        _analyses[analysis_id] = analysis_doc


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an analysis document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.get_document(analysis_id)
    else:
        return _analyses.get(analysis_id)


def delete_analysis(analysis_id: str) -> bool:
    """Delete an analysis document by ID."""
    if _use_couchbase():
        return CouchbaseQuery.delete_document(analysis_id)
    else:
        if analysis_id in _analyses:
            del _analyses[analysis_id]
            return True
        return False

