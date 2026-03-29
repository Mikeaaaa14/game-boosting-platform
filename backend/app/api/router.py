"""
Main API router module.
Combines all endpoint routers into a single API router.
"""

from fastapi import APIRouter

from app.api.endpoints import admin_router, auth_router, orders_router, users_router

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router)
api_router.include_router(orders_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
