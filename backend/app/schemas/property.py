"""Pydantic schemas for properties. Suffixed by purpose (rules/backend.md).

Never the same schema for request and response — a client must not set id,
tenant_id, status or timestamps on create.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.property import ListingType


class PropertyCreate(BaseModel):
    """What a client may send to create a property. No id/tenant/status/dates."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    property_type: str = Field(min_length=1, max_length=50)
    listing_type: ListingType = ListingType.buy
    price: Decimal | None = None
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    area_sqft: int | None = Field(default=None, ge=0)
    locality: str | None = Field(default=None, max_length=120)


class PropertyOut(BaseModel):
    """What the API returns."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    property_type: str
    listing_type: str
    status: str
    price: Decimal | None
    bedrooms: int | None
    bathrooms: int | None
    area_sqft: int | None
    locality: str | None


class PropertyPage(BaseModel):
    """The standard pagination envelope (04-api-spec.md §1)."""

    items: list[PropertyOut]
    total: int
    page: int
    page_size: int
