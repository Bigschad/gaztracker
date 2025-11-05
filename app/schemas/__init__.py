"""
Schemas Package

This package contains all Pydantic schemas for request/response validation.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    LoginRequest,
    LoginResponse,
    PasswordChange,
)

from app.schemas.rfid_tag import (
    RFIDTagCreate,
    RFIDTagUpdate,
    RFIDTagResponse,
    RFIDTagDetailResponse,
    RFIDTagListResponse,
    RFIDTagStatistics,
)

from app.schemas.palette import (
    PaletteCreate,
    PaletteUpdate,
    PaletteResponse,
    PaletteListResponse,
    PaletteScanRequest,
    PaletteScanResponse,
    PaletteStatistics,
)

from app.schemas.expedition import (
    ExpeditionCreate,
    ExpeditionUpdate,
    ExpeditionResponse,
    ExpeditionListResponse,
    ExpeditionDepartRequest,
    ExpeditionValidateRequest,
    ExpeditionStatistics,
)

from app.schemas.notification import (
    NotificationCreate,
    NotificationSendEmail,
    NotificationSendSMS,
    NotificationRetry,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatistics,
)


__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "LoginRequest",
    "LoginResponse",
    "PasswordChange",

    # RFID Tag schemas
    "RFIDTagCreate",
    "RFIDTagUpdate",
    "RFIDTagResponse",
    "RFIDTagDetailResponse",
    "RFIDTagListResponse",
    "RFIDTagStatistics",

    # Palette schemas
    "PaletteCreate",
    "PaletteUpdate",
    "PaletteResponse",
    "PaletteListResponse",
    "PaletteScanRequest",
    "PaletteScanResponse",
    "PaletteStatistics",

    # Expedition schemas
    "ExpeditionCreate",
    "ExpeditionUpdate",
    "ExpeditionResponse",
    "ExpeditionListResponse",
    "ExpeditionDepartRequest",
    "ExpeditionValidateRequest",
    "ExpeditionStatistics",

    # Notification schemas
    "NotificationCreate",
    "NotificationSendEmail",
    "NotificationSendSMS",
    "NotificationRetry",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationStatistics",
]
