"""
Authentication Middleware

FastAPI dependencies for JWT authentication and user extraction.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import asyncio

from app.database import get_db, get_sync_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.exceptions import InvalidTokenException, AuthenticationException
from app.utils.security import verify_token
from sqlalchemy import select
import uuid


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token (async version).
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session (async)
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails
        
    Example:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(token)
        return user
        
    except (InvalidTokenException, AuthenticationException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_sync(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_sync_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token (sync version).
    
    For use with sync database sessions (get_sync_db).
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session (sync)
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails
        
    Example:
        @app.get("/palettes")
        async def get_palettes(
            db: Session = Depends(get_sync_db),
            current_user: User = Depends(get_current_user_sync)
        ):
            return db.query(Palette).all()
    """
    try:
        token = credentials.credentials
        
        # Decode and verify token (sync operation)
        payload = verify_token(token, token_type="access")
        
        # Extract user ID
        user_id = uuid.UUID(payload.get("sub"))
        
        # Fetch user from database (sync query)
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User account is inactive")
        
        # Note: We skip Redis blacklist check in sync version for simplicity
        # If needed, you can add sync Redis client here
        
        return user
        
    except (InvalidTokenException, AuthenticationException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get current user (doesn't raise if no auth).
    
    Args:
        credentials: HTTP Bearer credentials (optional)
        db: Database session
        
    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(token)
        return user
    except:
        return None
