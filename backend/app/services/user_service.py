"""
User service module.
Business logic for user management and authentication.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import BoosterApplicationStatus, User, UserRole
from app.schemas.user import UserRegister, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user-related business logic.
    Handles authentication, registration, and user management.
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize user service with database session.
        
        Args:
            db: Async database session.
        """
        self._db = db
    
    async def register_user(
        self,
        user_data: UserRegister,
    ) -> User:
        """
        Register a new user.
        
        Args:
            user_data: Validated registration data.
            
        Returns:
            Created User instance.
            
        Raises:
            HTTPException: If email already exists.
        """
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册",
            )
        
        # Create user with hashed password
        requested_role = user_data.role
        role = UserRole.USER
        if requested_role != UserRole.USER:
            logger.warning(
                "Public registration attempted non-USER role=%s, forced to USER",
                requested_role.value,
            )

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            role=role,
            is_active=True,
            is_verified=False,
        )
        
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        
        logger.info(f"Registered new user: {user.email} with role {user.role.value}")
        
        return user

    async def ensure_default_admin(self) -> User:
        """Create default admin account if it does not exist."""
        admin = await self.get_user_by_email(settings.DEFAULT_ADMIN_EMAIL)
        if admin is not None:
            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                await self._db.flush()
                await self._db.refresh(admin)
            return admin

        admin = User(
            email=settings.DEFAULT_ADMIN_EMAIL,
            username=settings.DEFAULT_ADMIN_USERNAME,
            hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            booster_quota=0,
            booster_application_status=BoosterApplicationStatus.APPROVED,
        )
        self._db.add(admin)
        await self._db.flush()
        await self._db.refresh(admin)
        logger.warning("Default admin account created: %s", admin.email)
        return admin
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email.
            password: Plain text password.
            
        Returns:
            Authenticated User instance.
            
        Raises:
            HTTPException: If authentication fails.
        """
        if email.lower() == settings.DEFAULT_ADMIN_EMAIL.lower():
            try:
                await self.ensure_default_admin()
            except Exception:
                logger.exception("Failed to ensure default admin during login.")

        user = await self.get_user_by_email(email)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误",
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用",
            )
        
        logger.info(f"User authenticated: {email}")
        
        return user
    
    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email address.
        
        Args:
            email: User email.
            
        Returns:
            User instance or None if not found.
        """
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User instance or None if not found.
        """
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    def create_tokens(self, user: User) -> dict[str, Any]:
        """
        Create access and refresh tokens for user.
        
        Args:
            user: User to create tokens for.
            
        Returns:
            Dictionary containing tokens and metadata.
        """
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
            },
        )
        
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token.
            
        Returns:
            Dictionary containing new tokens and metadata.
            
        Raises:
            HTTPException: If refresh token is invalid.
        """
        payload = verify_token(refresh_token, token_type="refresh")
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或过期的刷新令牌",
            )
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌内容",
            )
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户标识",
            )
        
        user = await self.get_user_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用",
            )
        
        return self.create_tokens(user)
    
    async def update_user(
        self,
        user: User,
        update_data: UserUpdate,
    ) -> User:
        """
        Update user profile.
        
        Args:
            user: User to update.
            update_data: Update data.
            
        Returns:
            Updated User instance.
        """
        data = update_data.model_dump(exclude_unset=True)
        
        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await self._db.flush()
        await self._db.refresh(user)
        
        logger.info(f"Updated user profile: {user.email}")
        
        return user
    
    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        Change user password.
        
        Args:
            user: User to change password for.
            current_password: Current password for verification.
            new_password: New password.
            
        Returns:
            Updated User instance.
            
        Raises:
            HTTPException: If current password is incorrect.
        """
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误",
            )
        
        user.hashed_password = hash_password(new_password)
        
        await self._db.flush()
        await self._db.refresh(user)
        
        logger.info(f"Password changed for user: {user.email}")
        
        return user
    
    async def deactivate_user(
        self,
        user: User,
        admin: User,
    ) -> User:
        """
        Deactivate a user account (admin only).
        
        Args:
            user: User to deactivate.
            admin: Admin performing the action.
            
        Returns:
            Updated User instance.
            
        Raises:
            HTTPException: If not authorized.
        """
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己的账户",
            )
        
        user.is_active = False
        
        await self._db.flush()
        await self._db.refresh(user)
        
        logger.info(f"User deactivated by admin: {user.email}")
        
        return user

    async def submit_booster_application(
        self,
        user: User,
        game_name: str,
        current_rank: str,
        target_rank: str,
        proof_url: str,
        note: str | None = None,
    ) -> User:
        """Submit or update a user's booster application."""
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin account does not need to apply as booster.",
            )

        user.booster_application_status = BoosterApplicationStatus.PENDING
        user.booster_application_game = game_name
        user.booster_application_current_rank = current_rank
        user.booster_application_target_rank = target_rank
        user.booster_application_proof_url = proof_url
        user.booster_application_note = note
        user.reviewed_by_admin_id = None
        user.reviewed_at = None
        user.review_note = None

        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def list_booster_applications(
        self,
        status_filter: BoosterApplicationStatus | None = None,
    ) -> list[User]:
        """List booster application users for admin review."""
        query = select(User).where(User.role != UserRole.ADMIN)
        if status_filter is not None:
            query = query.where(User.booster_application_status == status_filter)
        query = query.order_by(User.created_at.desc())

        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def review_booster_application(
        self,
        admin: User,
        target_user_id: int,
        approve: bool,
        booster_quota: int,
        review_note: str | None = None,
    ) -> User:
        """Approve or reject a booster application."""
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can review applications.",
            )

        user = await self.get_user_by_id(target_user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot review admin account.",
            )

        user.reviewed_by_admin_id = admin.id
        user.reviewed_at = datetime.now(timezone.utc)
        user.review_note = review_note

        if approve:
            user.role = UserRole.BOOSTER
            user.booster_quota = booster_quota
            user.booster_application_status = BoosterApplicationStatus.APPROVED
            user.is_verified = True
        else:
            user.role = UserRole.USER
            user.booster_quota = 0
            user.booster_application_status = BoosterApplicationStatus.REJECTED

        await self._db.flush()
        await self._db.refresh(user)
        return user


def get_user_service(db: AsyncSession) -> UserService:
    """
    Factory function to create UserService instance.
    
    Args:
        db: Async database session.
        
    Returns:
        UserService instance.
    """
    return UserService(db)
