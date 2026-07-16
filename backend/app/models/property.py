"""Property + media models (PRD Module 9, 03-database-schema.md).

`properties` is tenant-owned: tenant_id NOT NULL, and RLS applied via the macro
in the migration. Status is the six-state enum from 06-property-approvals.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class PropertyStatus(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    published = "published"
    on_hold = "on_hold"
    sold = "sold"
    archived = "archived"


class ListingType(str, enum.Enum):
    buy = "buy"
    rent = "rent"


class Property(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "properties"

    # Tenant-owned. RLS keys off this column (core/rls.py).
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    property_type: Mapped[str] = mapped_column(String(50), nullable=False)
    listing_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default=ListingType.buy.value
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PropertyStatus.draft.value
    )

    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    bedrooms: Mapped[int | None] = mapped_column(Integer)
    bathrooms: Mapped[int | None] = mapped_column(Integer)
    area_sqft: Mapped[int | None] = mapped_column(Integer)
    locality: Mapped[str | None] = mapped_column(String(120))

    # Soft delete — CRM history survives (rules/database.md).
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    media: Mapped[list[PropertyMedia]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )


class PropertyMedia(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "property_media"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    property: Mapped[Property] = relationship(back_populates="media")
