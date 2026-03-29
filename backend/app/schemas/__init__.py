"""
Schemas package.
Pydantic models for API request/response validation.
"""

from app.schemas.order import (
    AIAnalysisResponse,
    OrderAnalyzeRequest,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
    UserBrief,
)
from app.schemas.user import (
    MessageResponse,
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.schemas.admin import (
    AdminOrderInterventionRequest,
    BoosterApplicationResponse,
    BoosterApplicationReviewRequest,
)

__all__ = [
    # Order schemas
    "OrderAnalyzeRequest",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListResponse",
    "AIAnalysisResponse",
    "UserBrief",
    # User schemas
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    "MessageResponse",
    # Admin/application schemas
    "BoosterApplicationResponse",
    "BoosterApplicationReviewRequest",
    "AdminOrderInterventionRequest",
]
