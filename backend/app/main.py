"""FastAPI entrypoint.

Layering (rules/backend.md, never skipped):
    Router → Service → Repository → DB

Routers parse, call ONE service method, and return. No business logic here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title="PropVista CRM API",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
)

# CORS — local dev only, so the Vite dev server can call the API. Production is
# same-origin (the SPA is served behind the same host), so this widens nothing
# there. Never use "*" with credentials in production.
if settings.environment == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe. Used by App Runner/ECS and by the Sprint 0 DoD."""
    return {"status": "ok"}
