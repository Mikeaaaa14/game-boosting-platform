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
from app.schemas.booster_service import (
    BoosterServiceCreate,
    BoosterServiceListResponse,
    BoosterServiceOrderCreate,
    BoosterServiceResponse,
    BoosterServiceUpdate,
)
from app.schemas.game import (
    GameCreate,
    GameListResponse,
    GameResponse,
    GameServiceTemplate,
    GameUpdate,
)
from app.schemas.search import SearchResponse, SearchType
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
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
from app.schemas.chat import (
    ChatMessageResponse,
    ChatUserBrief,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationParticipantResponse,
    ConversationReadRequest,
    ConversationResponse,
    InviteAdminResponse,
    MessageCreateRequest,
    UnreadSummaryResponse,
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
    # Booster service schemas
    "BoosterServiceCreate",
    "BoosterServiceUpdate",
    "BoosterServiceResponse",
    "BoosterServiceListResponse",
    "BoosterServiceOrderCreate",
    # Game schemas
    "GameServiceTemplate",
    "GameCreate",
    "GameUpdate",
    "GameResponse",
    "GameListResponse",
    # Search schemas
    "SearchType",
    "SearchResponse",
    # Review schemas
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewListResponse",
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
    # Chat schemas
    "ConversationCreateRequest",
    "MessageCreateRequest",
    "ConversationReadRequest",
    "ChatUserBrief",
    "ConversationParticipantResponse",
    "ConversationResponse",
    "ConversationListResponse",
    "ChatMessageResponse",
    "InviteAdminResponse",
    "UnreadSummaryResponse",
]
