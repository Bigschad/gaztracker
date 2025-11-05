"""
User Service

Business logic for user management operations (CRUD, password changes, etc.).
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
import uuid
import logging

from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    InvalidCredentialsException,
    ValidationException,
)
from app.config import settings


logger = logging.getLogger(__name__)


class UserService:
    """
    Service for handling user management operations.

    Provides methods for creating, reading, updating, and deleting users.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize user service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_user(
        self,
        user_data: UserCreate,
        created_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data
            created_by_id: ID of user creating this user (for audit)
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)

        Returns:
            User: Created user object

        Raises:
            DuplicateResourceException: If email already exists
            ValidationException: If validation fails
        """
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ResourceAlreadyExistsException(
                resource_type="User",
                field="email",
                value=user_data.email
            )

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user object
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            company_name=user_data.company_name,
            role=user_data.role,
            is_active=True,
            is_verified=False,  # Users start unverified
        )

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            # Log user creation
            await self._log_user_action(
                user_id=created_by_id,
                action="USER_CREATE",
                resource_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={"email": user.email, "role": user.role.value}
            )

            logger.info(f"User {user.id} created successfully")
            return user

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise ResourceAlreadyExistsException(
                resource_type="User",
                field="email",
                value=user_data.email
            )

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User: User object or None if not found
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User: User object or None if not found
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        List users with pagination and filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            role: Filter by role
            is_active: Filter by active status
            search: Search in email, first_name, last_name

        Returns:
            Tuple: (list of users, total count)
        """
        # Build query
        query = select(User)

        # Apply filters
        if role is not None:
            query = query.where(User.role == role)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (User.email.ilike(search_term)) |
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.company_name.ilike(search_term))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Order by creation date (newest first)
        query = query.order_by(User.created_at.desc())

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()

        logger.info(f"Listed {len(users)} users (page {page}, total {total})")
        return list(users), total

    async def update_user(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdate,
        updated_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Update user information.

        Args:
            user_id: User ID
            user_data: User update data
            updated_by_id: ID of user performing update (for audit)
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)

        Returns:
            User: Updated user object

        Raises:
            ResourceNotFoundException: If user not found
            DuplicateResourceException: If email already exists
        """
        # Get existing user
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(resource_type="User", resource_id=user_id)

        # Check if email is being changed and already exists
        if user_data.email and user_data.email != user.email:
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ResourceAlreadyExistsException(
                    resource_type="User",
                    field="email",
                    value=user_data.email
                )

        # Track changes for audit
        changes = {}

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and getattr(user, field) != value:
                changes[field] = {"old": getattr(user, field), "new": value}
                setattr(user, field, value)

        try:
            await self.db.commit()
            await self.db.refresh(user)

            # Log user update
            if changes:
                await self._log_user_action(
                    user_id=updated_by_id,
                    action="USER_UPDATE",
                    resource_id=str(user.id),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True,
                    additional_data={"changes": changes}
                )

            logger.info(f"User {user.id} updated successfully")
            return user

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to update user: {str(e)}")
            raise ResourceAlreadyExistsException(
                resource_type="User",
                field="email",
                value=user_data.email
            )

    async def delete_user(
        self,
        user_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Delete user (soft delete by setting is_active to False).

        Args:
            user_id: User ID
            deleted_by_id: ID of user performing deletion (for audit)
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)

        Raises:
            ResourceNotFoundException: If user not found
        """
        # Get existing user
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(resource_type="User", resource_id=user_id)

        # Soft delete by setting is_active to False
        user.is_active = False

        await self.db.commit()
        await self.db.refresh(user)

        # Log user deletion
        await self._log_user_action(
            user_id=deleted_by_id,
            action="USER_DELETE",
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={"email": user.email}
        )

        logger.info(f"User {user.id} deleted (soft delete)")

    async def change_password(
        self,
        user_id: uuid.UUID,
        password_data: PasswordChange,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Change user password.

        Args:
            user_id: User ID
            password_data: Password change data
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)

        Raises:
            ResourceNotFoundException: If user not found
            InvalidCredentialsException: If current password is incorrect
        """
        # Get existing user
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(resource_type="User", resource_id=user_id)

        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            # Log failed attempt
            await self._log_user_action(
                user_id=user_id,
                action="PASSWORD_CHANGE_FAILED",
                resource_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                additional_data={"reason": "Invalid current password"}
            )
            raise InvalidCredentialsException("Current password is incorrect")

        # Update password
        user.password_hash = hash_password(password_data.new_password)

        await self.db.commit()
        await self.db.refresh(user)

        # Log password change
        await self._log_user_action(
            user_id=user_id,
            action="PASSWORD_CHANGE",
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data=None
        )

        logger.info(f"Password changed for user {user.id}")

    async def _log_user_action(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        resource_id: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        success: bool,
        additional_data: Optional[dict] = None
    ) -> None:
        """
        Log user management action to audit log.

        Args:
            user_id: User ID performing the action
            action: Action performed
            resource_id: ID of resource being acted upon
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action was successful
            additional_data: Additional data to log
        """
        if not settings.ENABLE_AUDIT_LOG:
            return

        try:
            audit_log = AuditLog.create_log(
                user_id=user_id,
                action=action,
                resource_type="User",
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                additional_data=additional_data
            )

            self.db.add(audit_log)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log user action: {str(e)}")
            # Don't fail the operation if audit logging fails
            pass
