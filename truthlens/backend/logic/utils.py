"""Utility functions for ID generation and timestamps."""
import uuid
from datetime import datetime


def now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format with Z suffix."""
    return datetime.utcnow().isoformat() + "Z"


def make_id(prefix: str) -> str:
    """Generate a prefixed UUID for use as a document ID.
    
    Args:
        prefix: Document type prefix (e.g., 'user', 'upload', 'analysis')
    
    Returns:
        String in format 'prefix::uuid'
    """
    return f"{prefix}::{uuid.uuid4()}"
