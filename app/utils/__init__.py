"""
Utilities Package

This package contains utility modules for the GazTracker application.
"""

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    generate_otp,
    generate_rfid_tag,
    generate_expedition_reference,
)

from app.utils.exceptions import (
    GazTrackerException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ValidationException,
    to_http_exception,
)

from app.utils.constants import (
    USER_ROLES,
    PALETTE_TYPES,
    PALETTE_STATUSES,
    EXPEDITION_STATUSES,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
)


__all__ = [
    # Security functions
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "generate_otp",
    "generate_rfid_tag",
    "generate_expedition_reference",

    # Exceptions
    "GazTrackerException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ValidationException",
    "to_http_exception",

    # Constants
    "USER_ROLES",
    "PALETTE_TYPES",
    "PALETTE_STATUSES",
    "EXPEDITION_STATUSES",
    "ERROR_MESSAGES",
    "SUCCESS_MESSAGES",
]
