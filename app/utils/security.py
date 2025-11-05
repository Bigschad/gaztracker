"""
Security Utilities

This module contains security-related utilities including password hashing,
JWT token generation/validation, and OTP generation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import uuid

from app.config import settings
from app.utils.exceptions import InvalidTokenException


# =============================================================================
# Password Hashing
# =============================================================================

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT Token Management
# =============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        InvalidTokenException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise InvalidTokenException(f"Invalid token: {str(e)}")


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify a JWT token and check its type.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        InvalidTokenException: If token is invalid, expired, or wrong type
    """
    payload = decode_token(token)

    # Check token type
    if payload.get("type") != token_type:
        raise InvalidTokenException(f"Invalid token type. Expected {token_type}")

    # Check expiration
    exp = payload.get("exp")
    if exp is None:
        raise InvalidTokenException("Token has no expiration")

    if datetime.utcnow().timestamp() > exp:
        raise InvalidTokenException("Token has expired")

    return payload


def get_user_id_from_token(token: str) -> uuid.UUID:
    """
    Extract user ID from a JWT token.

    Args:
        token: JWT token string

    Returns:
        uuid.UUID: User ID

    Raises:
        InvalidTokenException: If token is invalid or missing user ID
    """
    payload = decode_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException("Token has no user ID")

    try:
        return uuid.UUID(user_id)
    except ValueError:
        raise InvalidTokenException("Invalid user ID in token")


# =============================================================================
# OTP Generation
# =============================================================================

def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric one-time password.

    Args:
        length: Length of the OTP (default: 6)

    Returns:
        str: Random numeric OTP
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_otp_with_expiry(
    length: int = 6,
    expiry_minutes: Optional[int] = None
) -> tuple[str, datetime]:
    """
    Generate an OTP with expiration time.

    Args:
        length: Length of the OTP (default: 6)
        expiry_minutes: Expiration time in minutes (default: from settings)

    Returns:
        tuple[str, datetime]: OTP and expiration datetime
    """
    otp = generate_otp(length)

    if expiry_minutes is None:
        expiry_minutes = settings.OTP_EXPIRY_MINUTES

    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    return otp, expiry


def verify_otp(
    provided_otp: str,
    stored_otp: str,
    expiry_time: datetime
) -> bool:
    """
    Verify an OTP code.

    Args:
        provided_otp: OTP provided by user
        stored_otp: OTP stored in database
        expiry_time: OTP expiration time

    Returns:
        bool: True if OTP is valid and not expired
    """
    # Check if expired
    if datetime.utcnow() > expiry_time:
        return False

    # Compare OTPs (constant-time comparison to prevent timing attacks)
    return secrets.compare_digest(provided_otp, stored_otp)


# =============================================================================
# RFID Tag Generation
# =============================================================================

def generate_rfid_tag(prefix: str = "GAZ", length: int = 12) -> str:
    """
    Generate a unique RFID tag.

    Args:
        prefix: RFID tag prefix (default: "GAZ")
        length: Total length of RFID tag (default: 12)

    Returns:
        str: Random RFID tag
    """
    # Calculate remaining length after prefix
    remaining_length = length - len(prefix)

    if remaining_length <= 0:
        raise ValueError("RFID length must be greater than prefix length")

    # Generate random alphanumeric string
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(characters) for _ in range(remaining_length))

    return f"{prefix}{random_part}"


# =============================================================================
# Expedition Reference Generation
# =============================================================================

def generate_expedition_reference(prefix: str = "EXP") -> str:
    """
    Generate a unique expedition reference number.

    Args:
        prefix: Reference prefix (default: "EXP")

    Returns:
        str: Unique reference number (format: EXP-YYYYMMDD-XXXXX)
    """
    # Get current date
    date_str = datetime.utcnow().strftime("%Y%m%d")

    # Generate random 5-digit number
    random_digits = ''.join(secrets.choice(string.digits) for _ in range(5))

    return f"{prefix}-{date_str}-{random_digits}"


# =============================================================================
# API Key Generation
# =============================================================================

def generate_api_key(length: int = 32) -> str:
    """
    Generate a random API key.

    Args:
        length: Length of the API key (default: 32)

    Returns:
        str: Random API key
    """
    return secrets.token_urlsafe(length)


# =============================================================================
# Password Validation
# =============================================================================

def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        tuple[bool, list[str]]: (is_valid, list of error messages)
    """
    errors = []

    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    # Check for uppercase letter
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase letter
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for digit
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character")

    return (len(errors) == 0, errors)


# =============================================================================
# Token Blacklist (for logout functionality)
# =============================================================================

async def add_token_to_blacklist(
    redis_client,
    token: str,
    expiry_seconds: Optional[int] = None
) -> None:
    """
    Add a token to the blacklist in Redis.

    Args:
        redis_client: Redis client instance
        token: JWT token to blacklist
        expiry_seconds: Optional expiration time (defaults to token expiry)
    """
    if expiry_seconds is None:
        # Decode token to get expiry
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            expiry_seconds = int(exp - datetime.utcnow().timestamp())

    if expiry_seconds and expiry_seconds > 0:
        await redis_client.setex(
            f"blacklist:{token}",
            expiry_seconds,
            "1"
        )


async def is_token_blacklisted(redis_client, token: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        redis_client: Redis client instance
        token: JWT token to check

    Returns:
        bool: True if token is blacklisted
    """
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None
