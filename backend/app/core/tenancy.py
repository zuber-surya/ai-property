"""Tenant context — sets the Postgres session variable RLS reads.

The RLS policy (core/rls.py) checks:
    tenant_id = current_setting('app.current_tenant_id')::uuid

So every request must set that variable on its DB session BEFORE any query, or
RLS sees no tenant and returns nothing. This function is the bridge.

`SET LOCAL` scopes the variable to the current transaction, so it cannot leak
into another request reusing the pooled connection — which would be a
cross-tenant leak of the worst kind.
"""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_current_tenant(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Set app.current_tenant_id for this session's transaction (RLS reads it)."""
    # Parameterised via set_config to avoid any interpolation into SQL.
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )
