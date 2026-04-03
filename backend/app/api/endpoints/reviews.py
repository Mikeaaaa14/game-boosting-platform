"""Review API endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DatabaseSession, OptionalCurrentUser
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.review_service import get_review_service

router = APIRouter(tags=["评价"])


@router.post(
    "/orders/{order_id}/reviews",
    response_model=ReviewResponse,
    status_code=201,
    summary="创建评价",
)
async def create_review(
    order_id: int,
    data: ReviewCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ReviewResponse:
    """Create a review for a completed order. Only order participants."""
    service = get_review_service(db)
    review = await service.create_review(order_id, current_user, data)
    return ReviewResponse.model_validate(review)


@router.put(
    "/orders/{order_id}/reviews",
    response_model=ReviewResponse,
    summary="修改评价",
)
async def update_review(
    order_id: int,
    data: ReviewUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ReviewResponse:
    """Update own review on an order."""
    service = get_review_service(db)
    review = await service.update_review(order_id, current_user, data)
    return ReviewResponse.model_validate(review)


@router.get(
    "/orders/{order_id}/reviews",
    response_model=ReviewListResponse,
    summary="获取订单评价",
)
async def get_order_reviews(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ReviewListResponse:
    """List reviews for an order."""
    service = get_review_service(db)
    reviews = await service.get_order_reviews(order_id)
    return ReviewListResponse(items=reviews, total=len(reviews))


@router.get(
    "/users/{user_id}/reviews",
    response_model=ReviewListResponse,
    summary="获取用户收到的评价",
)
async def get_user_reviews(
    user_id: int,
    db: DatabaseSession,
) -> ReviewListResponse:
    """List reviews received by a user. Public endpoint."""
    service = get_review_service(db)
    reviews, avg = await service.get_user_reviews(user_id)
    return ReviewListResponse(items=reviews, total=len(reviews), average_rating=avg)
