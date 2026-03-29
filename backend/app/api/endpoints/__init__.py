"""
API endpoints package.
Contains all API route handlers organized by resource.
"""

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.users import router as users_router

__all__ = [
    "auth_router",
    "orders_router",
    "users_router",
    "admin_router",
]
