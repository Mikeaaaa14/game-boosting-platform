"""Administrator endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DatabaseSession, get_current_admin
from app.models.order import OrderStatus
from app.models.user import BoosterApplicationStatus, User
from app.schemas.admin import (
    AdminOrderInterventionRequest,
    BoosterApplicationResponse,
    BoosterApplicationReviewRequest,
)
from app.schemas.order import OrderListResponse, OrderResponse
from app.services.order_service import get_order_service
from app.services.user_service import get_user_service

router = APIRouter(prefix="/admin", tags=["admin"])


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


@router.get("/users/applications", response_model=list[BoosterApplicationResponse])
async def list_user_applications(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
    status_filter: BoosterApplicationStatus | None = Query(default=None, alias="status"),
) -> list[BoosterApplicationResponse]:
    user_service = get_user_service(db)
    users = await user_service.list_booster_applications(status_filter=status_filter)
    return [_map_application_response(user) for user in users]


@router.put("/users/{user_id}/review", response_model=BoosterApplicationResponse)
async def review_user_application(
    user_id: int,
    payload: BoosterApplicationReviewRequest,
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> BoosterApplicationResponse:
    user_service = get_user_service(db)
    updated_user = await user_service.review_booster_application(
        admin=current_admin,
        target_user_id=user_id,
        approve=payload.approve,
        booster_quota=payload.booster_quota,
        review_note=payload.review_note,
    )
    return _map_application_response(updated_user)


@router.get("/orders", response_model=OrderListResponse)
async def list_all_orders_for_admin(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> OrderListResponse:
    order_service = get_order_service(db)
    orders, total = await order_service.list_orders(
        user=current_admin,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.put("/orders/{order_id}/intervene", response_model=OrderResponse)
async def intervene_order(
    order_id: int,
    payload: AdminOrderInterventionRequest,
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> OrderResponse:
    if payload.action not in (OrderStatus.CANCELLED, OrderStatus.DISPUTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin intervention only supports CANCELLED or DISPUTED.",
        )

    order_service = get_order_service(db)
    order = await order_service.get_order_by_id(order_id, current_admin)
    order.status = payload.action
    if payload.reason:
        order.notes = f"[ADMIN] {payload.reason}" + (f"\n{order.notes}" if order.notes else "")

    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)
