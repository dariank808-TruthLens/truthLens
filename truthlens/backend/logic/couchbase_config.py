"""Couchbase configuration and connection settings."""
import os
from typing import Optional


class CouchbaseConfig:
    """Couchbase connection configuration."""
    
    # Connection settings
    HOST: str = os.getenv("COUCHBASE_HOST", "couchbase://localhost")
    BUCKET_NAME: str = os.getenv("COUCHBASE_BUCKET", "truthlens")
    USERNAME: str = os.getenv("COUCHBASE_USER", "Administrator")
    PASSWORD: str = os.getenv("COUCHBASE_PASSWORD", "password")
    SCOPE: str = os.getenv("COUCHBASE_SCOPE", "_default")
    
    # Connection pool settings
    CONNECTION_TIMEOUT_MS: int = int(os.getenv("COUCHBASE_TIMEOUT", "5000"))
    MAX_RETRIES: int = int(os.getenv("COUCHBASE_MAX_RETRIES", "3"))
    
    # Feature flags
    USE_COUCHBASE: bool = os.getenv("USE_COUCHBASE", "true").lower() == "true"
    
    @classmethod
    def to_dict(cls) -> dict:
        """Return config as dict for easier inspection."""
        return {
            "host": cls.HOST,
            "bucket": cls.BUCKET_NAME,
            "username": cls.USERNAME,
            "scope": cls.SCOPE,
            "timeout_ms": cls.CONNECTION_TIMEOUT_MS,
            "use_couchbase": cls.USE_COUCHBASE,
        }
