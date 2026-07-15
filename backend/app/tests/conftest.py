"""Test fixtures. Integration tests run against the LIVE dev Postgres as the
non-superuser app_user — the only way an RLS test proves anything.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings

# Two tenants, always. A single-tenant fixture cannot catch a cross-tenant bug —
# and that is the bug that matters most (18-test-strategy.md §7).
TENANT_A = uuid.UUID("11111111-1111-1111-1111-111111111111")
TENANT_B = uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest_asyncio.fixture
async def app_engine():
    """Engine connecting as app_user — RLS APPLIES. Not the superuser."""
    engine = create_async_engine(get_settings().app_database_url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def app_sessionmaker(app_engine):
    return async_sessionmaker(app_engine, expire_on_commit=False)
