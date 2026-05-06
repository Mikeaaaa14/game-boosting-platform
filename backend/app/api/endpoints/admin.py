"""Administrator endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update

from app.api.chat_utils import send_order_system_message
from app.api.deps import DatabaseSession, get_current_admin
from app.models.booster_service import BoosterService
from app.models.order import Order, OrderStatus
from app.models.user import BoosterApplicationStatus, User
from app.schemas.admin import (
    AdminOrderInterventionRequest,
    BoosterApplicationResponse,
    BoosterApplicationReviewRequest,
)
from app.schemas.dashboard import (
    BoosterRankingResponse,
    GameDistributionResponse,
    OrderTrendResponse,
    OverviewStats,
    UserGrowthResponse,
)
from app.schemas.order import OrderListResponse, OrderResponse
from app.services.dashboard_service import get_dashboard_service
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
    allowed_actions = (OrderStatus.CANCELLED, OrderStatus.DISPUTED, OrderStatus.DELIVERED, OrderStatus.COMPLETED)
    if payload.action not in allowed_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员干预仅支持取消、争议、确认交付或完结订单",
        )

    # Lock the order row so this intervention cannot race with
    # complete_order / other interventions and double-increment order_count.
    order_result = await db.execute(
        select(Order).where(Order.id == order_id).with_for_update()
    )
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在",
        )

    previous_status = order.status
    order.status = payload.action
    if payload.reason:
        order.notes = f"[ADMIN] {payload.reason}" + (f"\n{order.notes}" if order.notes else "")

    if payload.action == OrderStatus.DELIVERED and previous_status != OrderStatus.DELIVERED:
        order.delivered_at = datetime.now(timezone.utc)

    if payload.action == OrderStatus.COMPLETED and previous_status != OrderStatus.COMPLETED:
        order.completed_at = datetime.now(timezone.utc)
        if order.service_id is not None:
            await db.execute(
                update(BoosterService)
                .where(BoosterService.id == order.service_id)
                .values(order_count=BoosterService.order_count + 1)
            )

    await db.flush()
    await db.refresh(order)
    await send_order_system_message(
        db=db,
        order_id=order.id,
        content=f"管理员已介入：{payload.reason}" if payload.reason else "管理员已介入处理订单",
        meta_json={
            "event": "admin_intervened",
            "order_id": order.id,
            "admin_id": current_admin.id,
            "action": payload.action.value,
            "reason": payload.reason,
        },
    )
    return OrderResponse.model_validate(order)


# =============================================================================
# Dashboard analytics endpoints
# =============================================================================


@router.get("/dashboard/overview", response_model=OverviewStats, summary="数据看板概览")
async def dashboard_overview(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> OverviewStats:
    """平台概览统计：用户数、订单数、收入等。"""
    svc = get_dashboard_service(db)
    return await svc.get_overview()


@router.get("/dashboard/order-trend", response_model=OrderTrendResponse, summary="订单趋势")
async def dashboard_order_trend(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
    period: str = Query(default="day", pattern="^(day|week|month)$"),
    days: int = Query(default=30, ge=7, le=365),
) -> OrderTrendResponse:
    """订单创建趋势图数据。"""
    svc = get_dashboard_service(db)
    return await svc.get_order_trend(period=period, days=days)


@router.get(
    "/dashboard/game-distribution",
    response_model=GameDistributionResponse,
    summary="游戏分布",
)
async def dashboard_game_distribution(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> GameDistributionResponse:
    """各游戏订单数量和收入分布。"""
    svc = get_dashboard_service(db)
    return await svc.get_game_distribution()


@router.get(
    "/dashboard/booster-ranking",
    response_model=BoosterRankingResponse,
    summary="代练排行榜",
)
async def dashboard_booster_ranking(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
    limit: int = Query(default=20, ge=1, le=50),
) -> BoosterRankingResponse:
    """代练排行榜（按完成数和信誉分）。"""
    svc = get_dashboard_service(db)
    return await svc.get_booster_ranking(limit=limit)


@router.get(
    "/dashboard/user-growth",
    response_model=UserGrowthResponse,
    summary="用户增长",
)
async def dashboard_user_growth(
    db: DatabaseSession,
    current_admin: Annotated[User, Depends(get_current_admin)],
    days: int = Query(default=30, ge=7, le=365),
) -> UserGrowthResponse:
    """用户注册增长趋势。"""
    svc = get_dashboard_service(db)
    return await svc.get_user_growth(days=days)
