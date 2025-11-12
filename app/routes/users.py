"""
User Routes

API endpoints for user management.
"""

from fastapi import APIRouter, Depends, status, Request, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import math

from app.database import get_db
from app.services.user_service import UserService
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    PasswordChange,
)
from app.middleware.auth_middleware import get_current_active_user
from app.middleware.rbac import require_admin, require_roles


router = APIRouter(prefix="/users", tags=["Users"])


# =============================================================================
# Helper Functions
# =============================================================================

def get_client_info(request: Request) -> tuple[str, str]:
    """
    Extract client IP and user agent from request.

    Args:
        request: FastAPI request object

    Returns:
        tuple: (ip_address, user_agent)
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", None)
    return ip_address, user_agent


# =============================================================================
# User Management Endpoints
# =============================================================================

@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Get a paginated list of users. Admin and logistics managers can view all users."
)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in email, name, company"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: AsyncSession = Depends(get_db)
) -> UserListResponse:
    """
    List users with pagination and filtering.

    Args:
        request: FastAPI request object
        page: Page number (1-indexed)
        page_size: Number of items per page
        role: Filter by role
        is_active: Filter by active status
        search: Search term
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserListResponse: Paginated list of users
    """
    # Initialize user service
    user_service = UserService(db)

    # Get users
    users, total = await user_service.list_users(
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
        search=search
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user. Admin only."
)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data
        request: FastAPI request object
        current_user: Current authenticated user (admin)
        db: Database session

    Returns:
        UserResponse: Created user

    Raises:
        DuplicateResourceException: If email already exists
    """
    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize user service
    user_service = UserService(db)

    # Create user
    user = await user_service.create_user(
        user_data=user_data,
        created_by_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User",
    description="Get user by ID. Admin, logistics managers, or the user themselves can view."
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse: User details

    Raises:
        ResourceNotFoundException: If user not found
        HTTPException: 403 if not authorized
    """
    # Initialize user service
    user_service = UserService(db)

    # Get user
    user = await user_service.get_user_by_id(user_id)
    if not user:
        from app.utils.exceptions import ResourceNotFoundException
        raise ResourceNotFoundException(resource_type="User", resource_id=user_id)

    # Check permissions: Admin, logistics manager, or the user themselves
    if not (
        current_user.role in [UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE] or
        current_user.id == user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User",
    description="Update user information. Admin or the user themselves can update."
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update user information.

    Args:
        user_id: User ID
        user_data: User update data
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse: Updated user

    Raises:
        ResourceNotFoundException: If user not found
        HTTPException: 403 if not authorized
    """
    # Check permissions: Admin or the user themselves
    # Non-admins cannot change role, is_active, or is_verified
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Non-admins cannot modify role, is_active, or is_verified
    if current_user.role != UserRole.ADMIN:
        if user_data.role is not None or user_data.is_active is not None or user_data.is_verified is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can modify role, active status, or verified status"
            )

    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize user service
    user_service = UserService(db)

    # Update user
    user = await user_service.update_user(
        user_id=user_id,
        user_data=user_data,
        updated_by_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete user (soft delete). Admin only."
)
async def delete_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete user (soft delete by setting is_active to False).

    Args:
        user_id: User ID
        request: FastAPI request object
        current_user: Current authenticated user (admin)
        db: Database session

    Raises:
        ResourceNotFoundException: If user not found
    """
    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize user service
    user_service = UserService(db)

    # Delete user
    await user_service.delete_user(
        user_id=user_id,
        deleted_by_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.put(
    "/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change Password",
    description="Change user password. Users can only change their own password."
)
async def change_password(
    user_id: UUID,
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Change user password.

    Args:
        user_id: User ID
        password_data: Password change data
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if not authorized
        ResourceNotFoundException: If user not found
        InvalidCredentialsException: If current password is incorrect
    """
    # Users can only change their own password
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only change your own password"
        )

    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize user service
    user_service = UserService(db)

    # Change password
    await user_service.change_password(
        user_id=user_id,
        password_data=password_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
