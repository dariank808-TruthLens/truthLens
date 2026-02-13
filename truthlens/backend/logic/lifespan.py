"""Application lifecycle management - startup and shutdown hooks."""
from .couchbase_client import CouchbaseClient
from .couchbase_config import CouchbaseConfig


async def on_startup() -> None:
    """Initialize services on application startup."""
    print("\n=== Application Startup ===")
    
    if CouchbaseConfig.USE_COUCHBASE:
        try:
            print("Connecting to Couchbase...")
            CouchbaseClient.connect()
            print("✓ Couchbase connected")
        except Exception as e:
            print(f"⚠ Couchbase connection failed: {e}")
            print("  Falling back to in-memory storage")
    else:
        print("ℹ Using in-memory storage (set USE_COUCHBASE=true to use Couchbase)")


async def on_shutdown() -> None:
    """Cleanup resources on application shutdown."""
    print("\n=== Application Shutdown ===")
    
    if CouchbaseClient.is_connected():
        CouchbaseClient.disconnect()
    
    print("✓ Shutdown complete")
