"""
API endpoints package.
Contains all API route handlers organized by resource.
"""

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.games import router as games_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.reviews import router as reviews_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.services import router as services_router
from app.api.endpoints.users import router as users_router

__all__ = [
    "auth_router",
    "chat_router",
    "games_router",
    "orders_router",
    "reviews_router",
    "search_router",
    "services_router",
    "users_router",
    "admin_router",
]
