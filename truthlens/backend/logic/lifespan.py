"""Application lifecycle management - startup and shutdown hooks.

This version is portal-aware: it no longer connects directly to Couchbase
from Python. Instead, it reports whether the Couchbase portal is enabled
so operators know whether persistence is using the TypeScript service or
the in-memory fallback.
"""
from . import portal_client


async def on_startup() -> None:
    """Initialize services on application startup."""
    print("\n=== Application Startup ===")

    if portal_client.is_enabled():
        print(
            f"INFO: Using Couchbase portal for persistence at "
            f"{portal_client.PORTAL_BASE_URL}"
        )
    else:
        print(
            "INFO: Using in-memory storage "
            "(set USE_PORTAL=true to enable the Couchbase portal)"
        )


async def on_shutdown() -> None:
    """Cleanup resources on application shutdown."""
    print("\n=== Application Shutdown ===")
    print("OK: Shutdown complete")
