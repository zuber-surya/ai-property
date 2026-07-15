"""Property business logic. Orchestrates the repository; writes no raw SQL."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.property import PropertyStatus
from app.repositories.property_repository import PropertyRepository
from app.schemas.property import PropertyCreate


class PropertyService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = PropertyRepository(session)

    async def create(self, tenant_id: uuid.UUID, data: PropertyCreate):
        """Create a property as a draft (status is service-owned, not client-set)."""
        prop = await self._repo.create(
            tenant_id, data.model_dump(exclude_unset=True) | _coerce(data)
        )
        await self._session.commit()
        return prop

    async def list_for_admin(self, page: int, page_size: int):
        return await self._repo.list_for_admin(page, page_size)

    async def list_published(self, page: int, page_size: int):
        return await self._repo.list_published(page, page_size)

    async def publish(self, property_id: uuid.UUID):
        """Publish a property. Raises if it isn't in this tenant (RLS → None → 404)."""
        prop = await self._repo.get(property_id)
        if prop is None:
            raise NotFoundError("Property not found.")
        prop = await self._repo.set_status(prop, PropertyStatus.published)
        await self._session.commit()
        # NOTE (slice): publishing should enqueue embed→index→match→notify via the
        # jobs pipeline (04-api-spec §8). Deferred until the worker lands; the
        # status flip is the visible half.
        return prop


def _coerce(data: PropertyCreate) -> dict:
    """listing_type is an enum in the schema; the column stores its value."""
    return {"listing_type": data.listing_type.value}
