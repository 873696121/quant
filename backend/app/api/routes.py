"""API routes aggregation module.

This module aggregates all API routes. Individual route modules
should be imported and included here.
"""

from fastapi import APIRouter

# Main API router
api_router = APIRouter(prefix="/api")

# Placeholder for health check (moved to main.py for /health)
# Additional routers will be added here:
# api_router.include_router(xxx_router, prefix="/xxx", tags=["xxx"])
