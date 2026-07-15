"""Property routers. Parse, call ONE service method, return. No logic here.

The tenancy dependency sets app.current_tenant_id on the session, so RLS scopes
every query below. For this slice the tenant is a fixed dev stub (get_dev_tenant);
real resolution (JWT for admin, domain for public) lands with auth in Sprint 1.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.tenancy import set_current_tenant
from app.schemas.property import PropertyCreate, PropertyOut, PropertyPage
from app.services.property_service import PropertyService

# --- dev tenancy stub (replaced by real resolution in Sprint 1) -----------
# A fixed seeded tenant. Auth/domain resolution is deferred (ADR: slice first),
# but RLS is NOT — the session var below is real and scopes every query.
DEV_TENANT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


async def tenant_session(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    await set_current_tenant(session, DEV_TENANT_ID)
    return session


admin_router = APIRouter(prefix="/admin/properties", tags=["admin:properties"])
public_router = APIRouter(prefix="/properties", tags=["properties"])


@admin_router.get("", response_model=PropertyPage)
async def list_admin_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(tenant_session),
) -> PropertyPage:
    items, total = await PropertyService(session).list_for_admin(page, page_size)
    return PropertyPage(items=items, total=total, page=page, page_size=page_size)


@admin_router.post("", response_model=PropertyOut, status_code=201)
async def create_property(
    body: PropertyCreate,
    session: AsyncSession = Depends(tenant_session),
) -> PropertyOut:
    return await PropertyService(session).create(DEV_TENANT_ID, body)


@admin_router.post("/{property_id}/publish", response_model=PropertyOut)
async def publish_property(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(tenant_session),
) -> PropertyOut:
    return await PropertyService(session).publish(property_id)


@public_router.get("", response_model=PropertyPage)
async def browse_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(tenant_session),
) -> PropertyPage:
    items, total = await PropertyService(session).list_published(page, page_size)
    return PropertyPage(items=items, total=total, page=page, page_size=page_size)
