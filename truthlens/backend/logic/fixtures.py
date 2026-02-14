"""Fixture loading for demo analysis data."""
import json
from typing import Optional, Dict, Any


def load_fixture_analysis() -> Optional[Dict[str, Any]]:
    """Load demo analysis fixture from JSON file.
    
    Used as fallback data when no real analysis backend is available.
    Attempts to load from backend/fixtures/analysis_example.json.
    
    Returns:
        Parsed JSON dict if file exists, None otherwise
    """
    try:
        with open("backend/fixtures/analysis_example.json", "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None
