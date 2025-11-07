"""
Authentication Routes

API endpoints for authentication (login, logout, token refresh, user info).
"""

from fastapi import APIRouter, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.utils.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
    InvalidTokenException,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


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
# Authentication Endpoints
# =============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password, returns access and refresh tokens"
)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: Login credentials (email and password)
        request: FastAPI request object
        db: Database session

    Returns:
        LoginResponse: User info and JWT tokens

    Raises:
        InvalidCredentialsException: If credentials are invalid
        InactiveUserException: If user account is inactive
    """
    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize auth service
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Create tokens
    tokens = await auth_service.create_tokens(user)

    # Return response
    return LoginResponse(
        user=UserResponse.model_validate(user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"]
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User Logout",
    description="Logout user by adding the access token to blacklist"
)
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Logout user by blacklisting their access token.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer token
        db: Database session

    Note:
        Gracefully handles expired tokens since user is logging out anyway.
    """
    # Extract token
    token = credentials.credentials

    # Extract client info
    ip_address, user_agent = get_client_info(request)

    # Initialize auth service
    auth_service = AuthService(db)

    try:
        # Get current user from token (validates token)
        user = await auth_service.get_current_user(token)

        # Logout user (blacklist token)
        await auth_service.logout_user(
            user_id=user.id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception:
        # If token is invalid or expired, that's fine - user is logging out
        # Just return success without blacklisting the token
        pass


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Get a new access token using a valid refresh token"
)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        refresh_request: Refresh token request
        db: Database session

    Returns:
        TokenResponse: New access token

    Raises:
        InvalidTokenException: If refresh token is invalid or expired
    """
    # Initialize auth service
    auth_service = AuthService(db)

    # Refresh access token
    return await auth_service.refresh_access_token(
        refresh_token=refresh_request.refresh_token
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get current authenticated user's information"
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        credentials: HTTP Bearer token
        db: Database session

    Returns:
        UserResponse: Current user information

    Raises:
        InvalidTokenException: If token is invalid
        AuthenticationException: If user not found or inactive
    """
    # Extract token
    token = credentials.credentials

    # Initialize auth service
    auth_service = AuthService(db)

    # Get current user
    user = await auth_service.get_current_user(token)

    return UserResponse.model_validate(user)
