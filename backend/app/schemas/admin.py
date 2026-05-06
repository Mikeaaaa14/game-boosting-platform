"""Admin and booster-application related schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus
from app.models.user import BoosterApplicationStatus, UserRole


class BoosterApplicationResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: UserRole
    status: BoosterApplicationStatus
    game_name: str | None = None
    current_rank: str | None = None
    target_rank: str | None = None
    proof_url: str | None = None
    note: str | None = None
    booster_quota: int
    reviewed_by_admin_id: int | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BoosterApplicationReviewRequest(BaseModel):
    approve: bool = Field(description="Approve or reject this application.")
    booster_quota: int = Field(default=1, ge=0, le=50)
    review_note: str | None = Field(default=None, max_length=500)


class AdminOrderInterventionRequest(BaseModel):
    action: OrderStatus = Field(description="Target order status after intervention.")
    reason: str | None = Field(default=None, max_length=500)

