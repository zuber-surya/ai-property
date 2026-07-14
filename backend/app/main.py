"""FastAPI entrypoint.

Layering (rules/backend.md, never skipped):
    Router → Service → Repository → DB

Routers parse, call ONE service method, and return. No business logic here.
"""

from fastapi import FastAPI

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

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe. Used by App Runner/ECS and by the Sprint 0 DoD."""
    return {"status": "ok"}
