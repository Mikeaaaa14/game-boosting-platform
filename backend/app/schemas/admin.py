"""Admin and booster-application related schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus
from app.models.user import BoosterApplicationStatus, UserRole


class BoosterApplicationResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: UserRole
    status: BoosterApplicationStatus
    game_name: Optional[str] = None
    current_rank: Optional[str] = None
    target_rank: Optional[str] = None
    proof_url: Optional[str] = None
    note: Optional[str] = None
    booster_quota: int
    reviewed_by_admin_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BoosterApplicationReviewRequest(BaseModel):
    approve: bool = Field(description="Approve or reject this application.")
    booster_quota: int = Field(default=1, ge=0, le=50)
    review_note: Optional[str] = Field(default=None, max_length=500)


class AdminOrderInterventionRequest(BaseModel):
    action: OrderStatus = Field(description="Target order status after intervention.")
    reason: Optional[str] = Field(default=None, max_length=500)

