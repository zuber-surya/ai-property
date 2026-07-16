"""The async engine + session for the REQUEST PATH.

Connects as `app_user` (non-superuser), so RLS applies (ADR-0003). Migrations and
admin tooling use a different, superuser connection that bypasses RLS.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_settings = get_settings()

# One engine for the whole app, connecting as the RLS-subject role.
engine = create_async_engine(_settings.app_database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: one session per request."""
    async with SessionLocal() as session:
        yield session
