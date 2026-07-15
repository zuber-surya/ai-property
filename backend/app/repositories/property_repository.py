"""Property data access — the ONLY place SQLAlchemy queries for properties live.

Every method is tenant-scoped by RLS (the session var is set by the router's
tenancy dependency). The explicit `deleted_at IS NULL` and `status` filters are
a SECOND layer on top of RLS, never the only one.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property, PropertyStatus


class PropertyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, tenant_id: uuid.UUID, data: dict) -> Property:
        """Insert a property. tenant_id is set here, never from the client."""
        prop = Property(tenant_id=tenant_id, status=PropertyStatus.draft.value, **data)
        self._session.add(prop)
        await self._session.flush()
        await self._session.refresh(prop)
        return prop

    async def list_for_admin(self, page: int, page_size: int) -> tuple[list[Property], int]:
        """All non-deleted properties for the current tenant (incl. drafts)."""
        base = select(Property).where(Property.deleted_at.is_(None))
        total = await self._session.scalar(select(func.count()).select_from(base.subquery()))
        rows = await self._session.scalars(
            base.order_by(Property.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows), int(total or 0)

    async def list_published(self, page: int, page_size: int) -> tuple[list[Property], int]:
        """Published, non-deleted properties — the public browse query."""
        base = select(Property).where(
            Property.deleted_at.is_(None),
            Property.status == PropertyStatus.published.value,
        )
        total = await self._session.scalar(select(func.count()).select_from(base.subquery()))
        rows = await self._session.scalars(
            base.order_by(Property.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows), int(total or 0)

    async def get(self, property_id: uuid.UUID) -> Property | None:
        return await self._session.scalar(
            select(Property).where(Property.id == property_id, Property.deleted_at.is_(None))
        )

    async def set_status(self, prop: Property, status: PropertyStatus) -> Property:
        prop.status = status.value
        await self._session.flush()
        await self._session.refresh(prop)
        return prop
