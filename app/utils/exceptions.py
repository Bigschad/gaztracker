"""
Custom Exceptions

This module defines custom exceptions for the GazTracker application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class GazTrackerException(Exception):
    """
    Base exception class for all GazTracker exceptions.

    Attributes:
        message: Error message
        code: Error code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


# =============================================================================
# Authentication & Authorization Exceptions
# =============================================================================

class AuthenticationException(GazTrackerException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(GazTrackerException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when credentials are invalid."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, details={"field": "credentials"})


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""

    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message, details={"field": "token"})


class InactiveUserException(AuthenticationException):
    """Raised when user account is inactive."""

    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message=message, details={"field": "user"})


# =============================================================================
# Resource Exceptions
# =============================================================================

class ResourceNotFoundException(GazTrackerException):
    """Raised when a resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any = None,
        message: Optional[str] = None
    ):
        if message is None:
            message = f"{resource_type} not found"
            if resource_id:
                message += f" (ID: {resource_id})"

        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": str(resource_id)}
        )


class ResourceAlreadyExistsException(GazTrackerException):
    """Raised when trying to create a resource that already exists."""

    def __init__(
        self,
        resource_type: str,
        field: str,
        value: Any,
        message: Optional[str] = None
    ):
        if message is None:
            message = f"{resource_type} with {field}='{value}' already exists"

        super().__init__(
            message=message,
            code="RESOURCE_ALREADY_EXISTS",
            details={"resource_type": resource_type, "field": field, "value": str(value)}
        )


# =============================================================================
# Validation Exceptions
# =============================================================================

class ValidationException(GazTrackerException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        field: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        validation_details = details or {}
        if field:
            validation_details["field"] = field

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=validation_details
        )


class InvalidStatusTransitionException(ValidationException):
    """Raised when status transition is invalid."""

    def __init__(
        self,
        current_status: str,
        new_status: str,
        resource_type: str = "Resource"
    ):
        message = f"Cannot transition {resource_type} from {current_status} to {new_status}"
        super().__init__(
            message=message,
            details={
                "current_status": current_status,
                "new_status": new_status,
                "resource_type": resource_type
            }
        )


class InvalidOTPException(ValidationException):
    """Raised when OTP is invalid."""

    def __init__(self, message: str = "Invalid or expired OTP"):
        super().__init__(message=message, field="otp")


# =============================================================================
# Business Logic Exceptions
# =============================================================================

class PaletteNotAvailableException(GazTrackerException):
    """Raised when palette is not available for assignment."""

    def __init__(
        self,
        palette_id: str,
        current_status: str,
        message: Optional[str] = None
    ):
        if message is None:
            message = f"Palette is not available (current status: {current_status})"

        super().__init__(
            message=message,
            code="PALETTE_NOT_AVAILABLE",
            details={"palette_id": palette_id, "current_status": current_status}
        )


class ExpeditionAlreadyDepartedException(GazTrackerException):
    """Raised when trying to modify an expedition that has already departed."""

    def __init__(self, expedition_id: str):
        super().__init__(
            message="Expedition has already departed and cannot be modified",
            code="EXPEDITION_ALREADY_DEPARTED",
            details={"expedition_id": expedition_id}
        )


class NoPalettesInExpeditionException(GazTrackerException):
    """Raised when trying to depart an expedition with no palettes."""

    def __init__(self, expedition_id: str):
        super().__init__(
            message="Cannot depart expedition with no palettes",
            code="NO_PALETTES_IN_EXPEDITION",
            details={"expedition_id": expedition_id}
        )


# =============================================================================
# Database Exceptions
# =============================================================================

class DatabaseException(GazTrackerException):
    """Raised when database operation fails."""

    def __init__(
        self,
        message: str = "Database error occurred",
        operation: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        db_details = details or {}
        if operation:
            db_details["operation"] = operation

        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=db_details
        )


# =============================================================================
# External Service Exceptions
# =============================================================================

class ExternalServiceException(GazTrackerException):
    """Raised when external service call fails."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        details: Optional[Dict] = None
    ):
        service_details = details or {}
        service_details["service"] = service_name

        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            details=service_details
        )


class NotificationException(ExternalServiceException):
    """Raised when notification sending fails."""

    def __init__(
        self,
        channel: str,
        message: str = "Failed to send notification",
        details: Optional[Dict] = None
    ):
        notification_details = details or {}
        notification_details["channel"] = channel

        super().__init__(
            service_name="notification",
            message=message,
            details=notification_details
        )


# =============================================================================
# Helper Functions for FastAPI HTTPExceptions
# =============================================================================

def to_http_exception(exc: GazTrackerException) -> HTTPException:
    """
    Convert a GazTrackerException to a FastAPI HTTPException.

    Args:
        exc: GazTrackerException instance

    Returns:
        HTTPException: FastAPI HTTPException
    """
    status_code_map = {
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "RESOURCE_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HTTPException(
        status_code=status_code,
        detail=exc.to_dict()
    )


def raise_http_exception(
    status_code: int,
    message: str,
    code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Raise an HTTPException with a structured error response.

    Args:
        status_code: HTTP status code
        message: Error message
        code: Error code
        details: Additional error details

    Raises:
        HTTPException: FastAPI HTTPException
    """
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": code,
            "message": message,
            "details": details or {}
        }
    )
