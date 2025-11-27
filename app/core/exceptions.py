"""
Core Exceptions Module

Re-exports exceptions from utils.exceptions for backward compatibility.
"""

from app.utils.exceptions import (
    ResourceNotFoundException as NotFoundException,
    ResourceAlreadyExistsException as DuplicateException,
    ValidationException,
    GazTrackerException as BusinessRuleException,
    AuthenticationException,
    AuthorizationException,
    ResourceAlreadyExistsException as ConflictException,
    ValidationException as BadRequestException,
    GazTrackerException as InternalServerException,
)

__all__ = [
    "NotFoundException",
    "DuplicateException",
    "ValidationException",
    "BusinessRuleException",
    "AuthenticationException",
    "AuthorizationException",
    "ConflictException",
    "BadRequestException",
    "InternalServerException",
]

