"""Aggregates every v1 router. Mounted at /api/v1 by main.py."""

from fastapi import APIRouter

from app.api.v1.properties import admin_router, public_router

api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(admin_router)
