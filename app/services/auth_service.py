"""
Authentication Service

Business logic for user authentication, token management, and user session handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
import uuid
import logging

from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserResponse, LoginResponse, TokenResponse
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    add_token_to_blacklist,
    is_token_blacklisted,
)
from app.utils.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
    InvalidTokenException,
    AuthenticationException,
)
from app.config import settings
from app.database import get_redis


logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling authentication operations.

    Provides methods for user authentication, token management,
    and session handling.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize authentication service.

        Args:
            db: Database session
        """
        self.db = db

    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Authenticate a user with email and password.

        Args:
            email: User email address
            password: Plain text password
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)

        Returns:
            User: Authenticated user object

        Raises:
            InvalidCredentialsException: If credentials are invalid
            InactiveUserException: If user account is inactive
        """
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        # Log authentication attempt
        await self._log_auth_attempt(
            user_id=user.id if user else None,
            email=email,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent,
            action="LOGIN_ATTEMPT"
        )

        # Validate user exists
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            raise InvalidCredentialsException("Invalid email or password")

        # Validate password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password for user {user.id}")
            raise InvalidCredentialsException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Authentication failed: inactive user {user.id}")
            raise InactiveUserException("User account is inactive")

        # Log successful authentication
        await self._log_auth_attempt(
            user_id=user.id,
            email=email,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent,
            action="LOGIN_SUCCESS"
        )

        logger.info(f"User {user.id} authenticated successfully")
        return user

    async def create_tokens(
        self,
        user: User
    ) -> Dict[str, Any]:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            dict: Dictionary containing access_token, refresh_token, token_type, expires_in
        """
        # Prepare token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        logger.info(f"Tokens created for user {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        }

    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> TokenResponse:
        """
        Refresh access token using a valid refresh token.

        Args:
            refresh_token: Refresh token string

        Returns:
            TokenResponse: New access token

        Raises:
            InvalidTokenException: If refresh token is invalid or expired
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, token_type="refresh")

            # Check if token is blacklisted
            redis = await get_redis()
            if await is_token_blacklisted(redis, refresh_token):
                raise InvalidTokenException("Token has been revoked")

            # Extract user info
            user_id = uuid.UUID(payload.get("sub"))

            # Verify user still exists and is active
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise InvalidTokenException("User not found")

            if not user.is_active:
                raise InactiveUserException("User account is inactive")

            # Create new access token
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
            new_access_token = create_access_token(token_data)

            logger.info(f"Access token refreshed for user {user.id}")

            return TokenResponse(
                access_token=new_access_token,
                token_type="bearer"
            )

        except JWTError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise InvalidTokenException(f"Invalid refresh token: {str(e)}")

    async def get_current_user(
        self,
        token: str
    ) -> User:
        """
        Get current user from access token.

        Args:
            token: Access token string

        Returns:
            User: Current user object

        Raises:
            InvalidTokenException: If token is invalid or expired
            AuthenticationException: If user not found or inactive
        """
        try:
            # Decode and verify token
            payload = verify_token(token, token_type="access")

            # Check if token is blacklisted
            redis = await get_redis()
            if await is_token_blacklisted(redis, token):
                raise InvalidTokenException("Token has been revoked")

            # Extract user ID
            user_id = uuid.UUID(payload.get("sub"))

            # Fetch user from database
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise AuthenticationException("User not found")

            if not user.is_active:
                raise InactiveUserException("User account is inactive")

            return user

        except (JWTError, ValueError) as e:
            logger.error(f"Get current user failed: {str(e)}")
            raise InvalidTokenException(f"Invalid token: {str(e)}")

    async def logout_user(
        self,
        user_id: uuid.UUID,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Logout user by adding token to blacklist.

        Args:
            user_id: User ID
            token: Access token to blacklist
            ip_address: Client IP address (for audit)
            user_agent: Client user agent (for audit)
        """
        # Add token to blacklist in Redis
        redis = await get_redis()
        await add_token_to_blacklist(redis, token)

        # Log logout event
        await self._log_auth_attempt(
            user_id=user_id,
            email=None,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent,
            action="LOGOUT"
        )

        logger.info(f"User {user_id} logged out successfully")

    async def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.

        Args:
            user: User object
            old_password: Current password
            new_password: New password

        Raises:
            InvalidCredentialsException: If old password is incorrect
        """
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsException("Current password is incorrect")

        # Update password
        from app.utils.security import hash_password
        user.password_hash = hash_password(new_password)

        await self.db.commit()
        await self.db.refresh(user)

        # Log password change
        await self._log_auth_attempt(
            user_id=user.id,
            email=user.email,
            success=True,
            ip_address=None,
            user_agent=None,
            action="PASSWORD_CHANGE"
        )

        logger.info(f"Password changed for user {user.id}")

    async def _log_auth_attempt(
        self,
        user_id: Optional[uuid.UUID],
        email: str,
        success: bool,
        ip_address: Optional[str],
        user_agent: Optional[str],
        action: str
    ) -> None:
        """
        Log authentication attempt to audit log.

        Args:
            user_id: User ID (if known)
            email: Email used for authentication
            success: Whether authentication was successful
            ip_address: Client IP address
            user_agent: Client user agent
            action: Action performed (LOGIN_ATTEMPT, LOGIN_SUCCESS, LOGOUT, etc.)
        """
        if not settings.ENABLE_AUDIT_LOG:
            return

        try:
            audit_log = AuditLog.create_log(
                user_id=user_id,
                action=action,
                resource_type="User",
                resource_id=str(user_id) if user_id else None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                additional_data={"email": email} if email else None
            )

            self.db.add(audit_log)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log auth attempt: {str(e)}")
            # Don't fail authentication if audit logging fails
            pass
