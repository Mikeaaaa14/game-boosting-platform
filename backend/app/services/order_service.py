"""
Order service module.
Business logic for order management operations.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import encrypt_text
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class for order-related business logic.
    Handles CRUD operations and business rules for orders.
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize order service with database session.
        
        Args:
            db: Async database session.
        """
        self._db = db
    
    async def create_order(
        self,
        order_data: OrderCreate,
        user: User,
    ) -> Order:
        """
        Create a new order for a user.
        
        Args:
            order_data: Validated order creation data.
            user: User creating the order.
            
        Returns:
            Created Order instance.
            
        Raises:
            HTTPException: If user is not allowed to create orders.
        """
        if user.role == UserRole.BOOSTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="代练账号不能创建订单",
            )
        
        order = Order(
            user_id=user.id,
            game_name=order_data.game_name,
            current_rank=order_data.current_rank,
            target_rank=order_data.target_rank,
            price=order_data.price,
            description_raw=order_data.description_raw,
            description_ai=order_data.description_ai,
            game_account=order_data.game_account,
            game_password=encrypt_text(order_data.game_password),
            priority=order_data.priority,
            notes=order_data.notes,
            status=OrderStatus.PENDING,
        )
        
        self._db.add(order)
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Created order {order.id} for user {user.id}")
        
        return order
    
    async def get_order_by_id(
        self,
        order_id: int,
        user: User | None = None,
    ) -> Order:
        """
        Get order by ID with access control.
        
        Args:
            order_id: Order ID to fetch.
            user: Optional user for access control.
            
        Returns:
            Order instance.
            
        Raises:
            HTTPException: If order not found or access denied.
        """
        result = await self._db.execute(
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.booster),
            )
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在",
            )
        
        # Access control
        if user is not None and user.role != UserRole.ADMIN:
            if user.role == UserRole.USER and order.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此订单",
                )
            if user.role == UserRole.BOOSTER:
                if order.booster_id is not None and order.booster_id != user.id:
                    if order.status != OrderStatus.PENDING:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="无权访问此订单",
                        )
        
        return order
    
    async def list_orders(
        self,
        user: User | None = None,
        game_name: str | None = None,
        status_filter: OrderStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """
        List orders with filtering and pagination.
        
        Args:
            user: Optional user for filtering (customers see own, boosters see available).
            game_name: Optional game name filter.
            status_filter: Optional status filter.
            page: Page number (1-indexed).
            page_size: Items per page.
            
        Returns:
            Tuple of (orders list, total count).
        """
        query = select(Order).options(
            selectinload(Order.user),
            selectinload(Order.booster),
        )
        count_query = select(func.count(Order.id))
        
        # Apply user-based filtering
        if user is not None:
            if user.role == UserRole.USER:
                # Users see only their own orders
                query = query.where(Order.user_id == user.id)
                count_query = count_query.where(Order.user_id == user.id)
            elif user.role == UserRole.BOOSTER:
                # Boosters see pending orders or their assigned orders
                query = query.where(
                    (Order.status == OrderStatus.PENDING) |
                    (Order.booster_id == user.id)
                )
                count_query = count_query.where(
                    (Order.status == OrderStatus.PENDING) |
                    (Order.booster_id == user.id)
                )
            # Admins see all orders (no filter)
        
        # Apply game name filter
        if game_name:
            query = query.where(Order.game_name.ilike(f"%{game_name}%"))
            count_query = count_query.where(Order.game_name.ilike(f"%{game_name}%"))
        
        # Apply status filter
        if status_filter:
            query = query.where(Order.status == status_filter)
            count_query = count_query.where(Order.status == status_filter)
        
        # Get total count
        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = query.order_by(Order.created_at.desc()).offset(offset).limit(page_size)
        
        # Execute query
        result = await self._db.execute(query)
        orders = list(result.scalars().all())
        
        return orders, total
    
    async def accept_order(
        self,
        order_id: int,
        booster: User,
    ) -> Order:
        """
        Accept an order as a booster.
        
        Args:
            order_id: Order ID to accept.
            booster: Booster user accepting the order.
            
        Returns:
            Updated Order instance.
            
        Raises:
            HTTPException: If order cannot be accepted.
        """
        if booster.role not in (UserRole.BOOSTER, UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有代练才能接单",
            )
        
        if booster.role == UserRole.BOOSTER:
            active_orders_count_result = await self._db.execute(
                select(func.count(Order.id)).where(
                    Order.booster_id == booster.id,
                    Order.status == OrderStatus.LOCKED,
                )
            )
            active_orders_count = int(active_orders_count_result.scalar() or 0)
            if booster.booster_quota <= active_orders_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Booster quota reached. Complete current orders first.",
                )

        result = await self._db.execute(
            select(Order)
            .where(Order.id == order_id)
            .with_for_update()
        )
        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许接单",
            )
        
        if order.booster_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已被其他代练接取",
            )
        
        if order.user_id == booster.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能接取自己的订单",
            )
        
        order.booster_id = booster.id
        order.status = OrderStatus.LOCKED
        order.locked_at = datetime.now(timezone.utc)
        
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Order {order_id} accepted by booster {booster.id}")
        
        return order
    
    async def complete_order(
        self,
        order_id: int,
        user: User,
    ) -> Order:
        """
        Mark an order as completed.
        
        Args:
            order_id: Order ID to complete.
            user: User completing the order (must be assigned booster or admin).
            
        Returns:
            Updated Order instance.
            
        Raises:
            HTTPException: If order cannot be completed.
        """
        order = await self.get_order_by_id(order_id)
        
        if order.status != OrderStatus.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有进行中的订单才能完成",
            )
        
        if user.role != UserRole.ADMIN and order.booster_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有接单代练才能完成订单",
            )
        
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now(timezone.utc)
        
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Order {order_id} completed by user {user.id}")
        
        return order
    
    async def cancel_order(
        self,
        order_id: int,
        user: User,
    ) -> Order:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel.
            user: User cancelling the order.
            
        Returns:
            Updated Order instance.
            
        Raises:
            HTTPException: If order cannot be cancelled.
        """
        order = await self.get_order_by_id(order_id)
        
        # Only pending orders can be cancelled by users
        if order.status not in (OrderStatus.PENDING, OrderStatus.LOCKED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许取消",
            )
        
        # Access control
        if user.role != UserRole.ADMIN:
            if order.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有订单创建者才能取消订单",
                )
            if order.status == OrderStatus.LOCKED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="订单已被接取，请联系客服处理",
                )
        
        order.status = OrderStatus.CANCELLED
        
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Order {order_id} cancelled by user {user.id}")
        
        return order
    
    async def dispute_order(
        self,
        order_id: int,
        user: User,
        reason: str | None = None,
    ) -> Order:
        """
        Mark an order as disputed.
        
        Args:
            order_id: Order ID to dispute.
            user: User raising the dispute.
            reason: Optional dispute reason.
            
        Returns:
            Updated Order instance.
            
        Raises:
            HTTPException: If order cannot be disputed.
        """
        order = await self.get_order_by_id(order_id)
        
        if order.status not in (OrderStatus.LOCKED, OrderStatus.COMPLETED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有进行中或已完成的订单才能发起争议",
            )
        
        # Only order owner, booster, or admin can dispute
        if user.role != UserRole.ADMIN:
            if order.user_id != user.id and order.booster_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权对此订单发起争议",
                )
        
        order.status = OrderStatus.DISPUTED
        if reason:
            order.notes = f"争议原因: {reason}" + (f"\n{order.notes}" if order.notes else "")
        
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Order {order_id} disputed by user {user.id}")
        
        return order
    
    async def update_order(
        self,
        order_id: int,
        order_data: OrderUpdate,
        user: User,
    ) -> Order:
        """
        Update an order.
        
        Args:
            order_id: Order ID to update.
            order_data: Update data.
            user: User making the update.
            
        Returns:
            Updated Order instance.
            
        Raises:
            HTTPException: If order cannot be updated.
        """
        order = await self.get_order_by_id(order_id)
        
        # Only pending orders can be updated
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有待接单的订单才能修改",
            )
        
        # Access control
        if user.role != UserRole.ADMIN and order.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有订单创建者才能修改订单",
            )
        
        # Update fields
        update_data = order_data.model_dump(exclude_unset=True)
        if "game_password" in update_data:
            update_data["game_password"] = encrypt_text(update_data["game_password"])

        for field, value in update_data.items():
            if hasattr(order, field):
                setattr(order, field, value)
        
        await self._db.flush()
        await self._db.refresh(order)
        
        logger.info(f"Order {order_id} updated by user {user.id}")
        
        return order


def get_order_service(db: AsyncSession) -> OrderService:
    """
    Factory function to create OrderService instance.
    
    Args:
        db: Async database session.
        
    Returns:
        OrderService instance.
    """
    return OrderService(db)
