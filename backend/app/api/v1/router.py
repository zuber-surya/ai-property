"""Aggregates every v1 router. Mounted at /api/v1 by main.py."""

from fastapi import APIRouter

api_router = APIRouter()

# Routers are added here as each module lands (properties, leads, auth, ai/...).
# Keep this file boring: it wires, it does not decide.
