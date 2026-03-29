"""User profile and booster-application endpoints."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.deps import CurrentUser, DatabaseSession
from app.core.config import settings
from app.models.user import BoosterApplicationStatus, User
from app.schemas.admin import BoosterApplicationResponse
from app.services.user_service import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


def _map_application_response(user: User) -> BoosterApplicationResponse:
    return BoosterApplicationResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.booster_application_status,
        game_name=user.booster_application_game,
        current_rank=user.booster_application_current_rank,
        target_rank=user.booster_application_target_rank,
        proof_url=user.booster_application_proof_url,
        note=user.booster_application_note,
        booster_quota=user.booster_quota,
        reviewed_by_admin_id=user.reviewed_by_admin_id,
        reviewed_at=user.reviewed_at,
        review_note=user.review_note,
    )


@router.get("/me/booster-application", response_model=BoosterApplicationResponse)
async def get_my_booster_application(current_user: CurrentUser) -> BoosterApplicationResponse:
    return _map_application_response(current_user)


@router.post("/booster-application", response_model=BoosterApplicationResponse)
async def submit_booster_application(
    db: DatabaseSession,
    current_user: CurrentUser,
    game_name: str = Form(..., min_length=1, max_length=100),
    current_rank: str = Form(..., min_length=1, max_length=50),
    target_rank: str = Form(..., min_length=1, max_length=50),
    note: str | None = Form(default=None, max_length=500),
    proof_image: UploadFile = File(...),
) -> BoosterApplicationResponse:
    if current_user.booster_application_status == BoosterApplicationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your booster application is already approved.",
        )

    if not proof_image.content_type or not proof_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proof file must be an image.",
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(proof_image.filename or "").suffix or ".png"
    file_name = f"booster-proof-{current_user.id}-{uuid4().hex}{suffix}"
    file_path = upload_dir / file_name
    file_path.write_bytes(await proof_image.read())
    proof_url = f"/uploads/{file_name}"

    user_service = get_user_service(db)
    updated_user = await user_service.submit_booster_application(
        user=current_user,
        game_name=game_name,
        current_rank=current_rank,
        target_rank=target_rank,
        proof_url=proof_url,
        note=note,
    )
    return _map_application_response(updated_user)
