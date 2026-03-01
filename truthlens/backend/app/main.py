from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router
from ..graphql.graphql_router import graphql_app
from ..logic.lifespan import on_startup, on_shutdown
from ..logic import portal_client

app = FastAPI()

# Register startup and shutdown events
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

# Allow local frontend dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# mount GraphQL endpoint at /graphql
app.mount("/graphql", graphql_app)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend! GraphQL available at /graphql"}


@app.get("/health")
def health():
    """Health check. If USE_PORTAL is set, also reports portal connectivity."""
    payload = {"status": "ok"}
    if portal_client.is_enabled():
        ok, msg = portal_client.check_health()
        payload["portal"] = "ok" if ok else msg
    return payload