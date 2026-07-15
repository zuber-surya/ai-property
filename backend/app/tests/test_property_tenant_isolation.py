"""ADR-0003: tenant isolation must hold AT THE DB LAYER, not just the API layer.

These run as `app_user` (non-superuser), so RLS is genuinely in force. If the
app connected as a superuser, every one of these would falsely pass — which is
exactly why conftest uses app_user.

The proof that matters: with the tenant session var set to A, a B-owned row is
INVISIBLE even to a direct repository query. RLS, not application `if`s.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.core.tenancy import set_current_tenant
from app.repositories.property_repository import PropertyRepository
from app.schemas.property import PropertyCreate
from app.tests.conftest import TENANT_A, TENANT_B

_A_PROPERTY = PropertyCreate(title="Tenant A villa", property_type="villa")
_B_PROPERTY = PropertyCreate(title="Tenant B flat", property_type="apartment")


async def _create(sessionmaker, tenant_id, payload):
    async with sessionmaker() as s:
        await set_current_tenant(s, tenant_id)
        repo = PropertyRepository(s)
        prop = await repo.create(tenant_id, payload.model_dump() | {"listing_type": "buy"})
        await s.commit()
        return prop.id


@pytest.mark.asyncio
async def test_tenant_A_cannot_see_tenant_B_rows(app_sessionmaker):
    """TC-TENANT-01 (properties): A's session cannot read B's property. DB layer."""
    a_id = await _create(app_sessionmaker, TENANT_A, _A_PROPERTY)
    b_id = await _create(app_sessionmaker, TENANT_B, _B_PROPERTY)

    async with app_sessionmaker() as s:
        await set_current_tenant(s, TENANT_A)
        repo = PropertyRepository(s)
        items, _ = await repo.list_for_admin(page=1, page_size=100)
        ids = {p.id for p in items}

    assert a_id in ids, "A must see its own row"
    assert b_id not in ids, "RLS FAILED: A can see B's row — cross-tenant leak"

    # And a direct get() of B's id from A's session must return nothing.
    async with app_sessionmaker() as s:
        await set_current_tenant(s, TENANT_A)
        leaked = await PropertyRepository(s).get(b_id)
    assert leaked is None, "RLS FAILED: A fetched B's row by id"


@pytest.mark.asyncio
async def test_no_tenant_context_sees_nothing(app_sessionmaker):
    """With no tenant var set, RLS returns zero rows — fail closed, not open."""
    await _create(app_sessionmaker, TENANT_A, _A_PROPERTY)

    async with app_sessionmaker() as s:
        # Deliberately do NOT call set_current_tenant.
        count = await s.scalar(text("SELECT count(*) FROM properties"))
    assert count == 0, "RLS must fail CLOSED when no tenant is set, not expose all"


@pytest.mark.asyncio
async def test_A_cannot_write_into_B(app_sessionmaker):
    """RLS WITH CHECK: A's session cannot INSERT a row tagged as B's tenant."""
    async with app_sessionmaker() as s:
        await set_current_tenant(s, TENANT_A)
        repo = PropertyRepository(s)
        # Try to smuggle in a row owned by B while scoped to A. RLS WITH CHECK
        # rejects it — "new row violates row-level security policy".
        with pytest.raises(DBAPIError):
            await repo.create(TENANT_B, _B_PROPERTY.model_dump() | {"listing_type": "buy"})
            await s.flush()
