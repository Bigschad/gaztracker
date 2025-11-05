"""
Notification Schemas

Pydantic schemas for Notification model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID

from app.models.notification import NotificationType, NotificationStatus, NotificationChannel


# =============================================================================
# Base Schemas
# =============================================================================

class NotificationBase(BaseModel):
    """Base notification schema with common fields."""

    type: NotificationType = Field(..., description="Type of notification")
    channel: NotificationChannel = Field(default=NotificationChannel.EMAIL, description="Delivery channel")
    recipient_email: Optional[EmailStr] = Field(None, description="Recipient email address")
    recipient_phone: Optional[str] = Field(None, max_length=20, description="Recipient phone number")
    subject: Optional[str] = Field(None, max_length=255, description="Notification subject")
    message: str = Field(..., max_length=5000, description="Notification message")


# =============================================================================
# Request Schemas
# =============================================================================

class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""

    expedition_id: Optional[UUID] = Field(None, description="Related expedition ID")
    palette_id: Optional[UUID] = Field(None, description="Related palette ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "EXPEDITION_DEPART",
                "channel": "EMAIL",
                "recipient_email": "client@example.com",
                "subject": "Votre expédition est partie",
                "message": "Votre expédition EXP-20240115-12345 est partie et arrivera bientôt.",
                "expedition_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class NotificationSendEmail(BaseModel):
    """Schema for sending an email notification."""

    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., max_length=255, description="Email subject")
    body: str = Field(..., max_length=10000, description="Email body (supports HTML)")
    is_html: bool = Field(default=True, description="Whether body is HTML")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_email": "client@example.com",
                "subject": "Confirmation d'expédition",
                "body": "<p>Votre expédition est en route.</p>",
                "is_html": True
            }
        }
    )


class NotificationSendSMS(BaseModel):
    """Schema for sending an SMS notification."""

    to_phone: str = Field(..., max_length=20, description="Recipient phone number (E.164 format)")
    message: str = Field(..., max_length=160, description="SMS message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_phone": "+33612345678",
                "message": "Votre expédition EXP-20240115-12345 est arrivée. Code OTP: 123456"
            }
        }
    )


class NotificationRetry(BaseModel):
    """Schema for retrying a failed notification."""

    notification_id: UUID = Field(..., description="Notification ID to retry")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: UUID = Field(..., description="Notification ID")
    status: NotificationStatus = Field(..., description="Delivery status")
    expedition_id: Optional[UUID] = Field(None, description="Related expedition ID")
    palette_id: Optional[UUID] = Field(None, description="Related palette ID")
    sent_at: Optional[datetime] = Field(None, description="When notification was sent")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: str = Field(default="0", description="Number of retry attempts")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "EXPEDITION_DEPART",
                "status": "SENT",
                "channel": "EMAIL",
                "recipient_email": "client@example.com",
                "recipient_phone": None,
                "subject": "Expédition partie",
                "message": "Votre expédition est en route.",
                "expedition_id": "123e4567-e89b-12d3-a456-426614174001",
                "palette_id": None,
                "sent_at": "2024-01-15T10:00:00Z",
                "error_message": None,
                "retry_count": "0",
                "created_at": "2024-01-15T09:59:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }
    )


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response."""

    total: int = Field(..., description="Total number of notifications")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    notifications: list[NotificationResponse] = Field(..., description="List of notifications")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 50,
                "page": 1,
                "page_size": 20,
                "notifications": []
            }
        }
    )


class NotificationStatistics(BaseModel):
    """Schema for notification statistics."""

    total_notifications: int = Field(..., description="Total number of notifications")
    by_status: dict[str, int] = Field(..., description="Count by status")
    by_type: dict[str, int] = Field(..., description="Count by type")
    by_channel: dict[str, int] = Field(..., description="Count by channel")
    success_rate: float = Field(..., description="Success rate percentage")
    failed_count: int = Field(..., description="Number of failed notifications")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_notifications": 500,
                "by_status": {
                    "SENT": 450,
                    "FAILED": 30,
                    "PENDING": 20
                },
                "by_type": {
                    "EXPEDITION_DEPART": 150,
                    "CONFIRMATION_LIVRAISON": 120,
                    "ALERTE_RETARD": 50
                },
                "by_channel": {
                    "EMAIL": 400,
                    "SMS": 80,
                    "BOTH": 20
                },
                "success_rate": 90.0,
                "failed_count": 30
            }
        }
    )
