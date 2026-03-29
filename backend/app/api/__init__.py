"""
API package.
Contains all API routes, dependencies, and endpoint handlers.
"""

from app.api.router import api_router
from app.api.deps import (
    CurrentUser,
    CurrentActiveUser,
    CurrentVerifiedUser,
    OptionalCurrentUser,
    DatabaseSession,
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_optional_current_user,
    get_current_booster,
    get_current_admin,
    require_role,
)

__all__ = [
    "api_router",
    "CurrentUser",
    "CurrentActiveUser",
    "CurrentVerifiedUser",
    "OptionalCurrentUser",
    "DatabaseSession",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_optional_current_user",
    "get_current_booster",
    "get_current_admin",
    "require_role",
]
