"""
Orders API endpoints.
Handles order creation, listing, and management operations.
"""

import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentUser,
    DatabaseSession,
    OptionalCurrentUser,
    get_current_booster,
    get_current_user,
)
from app.models.order import OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import (
    AIAnalysisResponse,
    OrderAnalyzeRequest,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
)
from app.schemas.user import MessageResponse
from app.services.ai_service import LLMService, get_llm_service
from app.services.order_service import OrderService, get_order_service

router = APIRouter(prefix="/orders", tags=["订单"])


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    summary="AI分析需求",
    description="使用AI分析用户的游戏代练需求描述，提取结构化信息",
)
async def analyze_requirement(
    request: OrderAnalyzeRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
) -> AIAnalysisResponse:
    """
    Analyze user requirement using AI.
    
    - **description**: Natural language description of boosting requirements
    
    Returns structured data extracted from the description including:
    - game_name: Name of the game
    - current_rank: Current player rank
    - target_rank: Desired rank
    - price: Budget amount
    - role: Game role/position
    - server: Game server/region
    - is_risky: Flag for prohibited content
    """
    result = await llm_service.analyze_requirement(request.description)
    
    # Check for risky content
    if result.get("is_risky", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需求描述包含违规内容，请修改后重试",
        )
    
    return AIAnalysisResponse(
        game_name=result.get("game_name"),
        current_rank=result.get("current_rank"),
        target_rank=result.get("target_rank"),
        price=result.get("price"),
        role=result.get("role"),
        server=result.get("server"),
        is_risky=result.get("is_risky", False),
    )


@router.post(
    "/create",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
    description="根据结构化数据创建新的代练订单",
)
async def create_order(
    order_data: OrderCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrderResponse:
    """
    Create a new boosting order.
    
    Requires authentication. Users cannot create orders with BOOSTER role.
    
    - **game_name**: Name of the game
    - **current_rank**: Current player rank
    - **target_rank**: Desired rank
    - **price**: Order price
    - **description_raw**: Original description (optional)
    - **game_account**: Game account credentials (optional)
    - **game_password**: Game password (optional)
    """
    order_service = get_order_service(db)
    
    order = await order_service.create_order(order_data, current_user)
    
    return OrderResponse.model_validate(order)


@router.get(
    "/",
    response_model=OrderListResponse,
    summary="获取订单列表",
    description="获取订单列表，支持分页和筛选",
)
async def list_orders(
    current_user: CurrentUser,
    db: DatabaseSession,
    game_name: Annotated[
        Optional[str],
        Query(description="按游戏名称筛选", max_length=100),
    ] = None,
    status_filter: Annotated[
        Optional[OrderStatus],
        Query(alias="status", description="按订单状态筛选"),
    ] = None,
    page: Annotated[
        int,
        Query(ge=1, description="页码"),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="每页数量"),
    ] = 20,
) -> OrderListResponse:
    """
    List orders with filtering and pagination.
    
    - Users see only their own orders
    - Boosters see pending orders and their assigned orders
    - Admins see all orders
    
    Filters:
    - **game_name**: Filter by game name (partial match)
    - **status**: Filter by order status
    
    Pagination:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    order_service = get_order_service(db)
    
    orders, total = await order_service.list_orders(
        user=current_user,
        game_name=game_name,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    
    # Calculate total pages
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="获取订单详情",
    description="根据订单ID获取订单详细信息",
)
async def get_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrderResponse:
    """
    Get order details by ID.
    
    Access control:
    - Users can only view their own orders
    - Boosters can view pending orders or their assigned orders
    - Admins can view all orders
    """
    order_service = get_order_service(db)
    
    order = await order_service.get_order_by_id(order_id, current_user)
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="更新订单",
    description="更新订单信息（仅限待接单状态）",
)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrderResponse:
    """
    Update order details.
    
    Only pending orders can be updated.
    Only order owner or admin can update.
    """
    order_service = get_order_service(db)
    
    order = await order_service.update_order(order_id, order_data, current_user)
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}/accept",
    response_model=OrderResponse,
    summary="接受订单",
    description="代练接受订单（仅限代练角色）",
)
async def accept_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_booster)],
    db: DatabaseSession,
) -> OrderResponse:
    """
    Accept an order as a booster.
    
    - Only users with BOOSTER or ADMIN role can accept orders
    - Only PENDING orders can be accepted
    - Cannot accept your own order
    """
    # Additional role check (get_current_booster already validates)
    if current_user.role not in (UserRole.BOOSTER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有代练才能接单",
        )
    
    order_service = get_order_service(db)
    
    order = await order_service.accept_order(order_id, current_user)
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}/complete",
    response_model=OrderResponse,
    summary="完成订单",
    description="标记订单为已完成",
)
async def complete_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrderResponse:
    """
    Mark order as completed.
    
    - Only assigned booster or admin can complete
    - Only LOCKED orders can be completed
    """
    order_service = get_order_service(db)
    
    order = await order_service.complete_order(order_id, current_user)
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="取消订单",
    description="取消订单（仅限待接单状态）",
)
async def cancel_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrderResponse:
    """
    Cancel an order.
    
    - Only order owner or admin can cancel
    - Only PENDING orders can be cancelled by users
    - Admin can cancel PENDING or LOCKED orders
    """
    order_service = get_order_service(db)
    
    order = await order_service.cancel_order(order_id, current_user)
    
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}/dispute",
    response_model=OrderResponse,
    summary="发起争议",
    description="对订单发起争议",
)
async def dispute_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
    reason: Annotated[
        Optional[str],
        Query(description="争议原因", max_length=500),
    ] = None,
) -> OrderResponse:
    """
    Raise a dispute on an order.
    
    - Only order owner, assigned booster, or admin can dispute
    - Only LOCKED or COMPLETED orders can be disputed
    """
    order_service = get_order_service(db)
    
    order = await order_service.dispute_order(order_id, current_user, reason)
    
    return OrderResponse.model_validate(order)


@router.delete(
    "/{order_id}",
    response_model=MessageResponse,
    summary="删除订单",
    description="删除订单（仅限管理员）",
)
async def delete_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> MessageResponse:
    """
    Delete an order (admin only).
    
    This is a soft operation - prefer using cancel/dispute for normal workflows.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有管理员才能删除订单",
        )
    
    order_service = get_order_service(db)
    
    # Verify order exists
    order = await order_service.get_order_by_id(order_id)
    
    # Delete order
    await db.delete(order)
    await db.flush()
    
    return MessageResponse(message="订单已删除", success=True)
