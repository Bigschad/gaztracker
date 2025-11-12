"""
Models Package

This package contains all SQLAlchemy models for the GazTracker application.
"""

from app.models.user import User, UserRole
from app.models.palette import Palette, PaletteType, PaletteStatus
from app.models.rfid_tag import RFIDTag, RFIDTagStatus
from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationChannel
from app.models.audit import AuditLog
from app.models.partner import Partner, PartnerType
from app.models.contact import Contact


__all__ = [
    # Models
    "User",
    "Palette",
    "RFIDTag",
    "Expedition",
    "PaletteMovement",
    "Notification",
    "AuditLog",
    "Partner",
    "Contact",

    # Enums
    "UserRole",
    "PaletteType",
    "PaletteStatus",
    "RFIDTagStatus",
    "ExpeditionStatus",
    "MovementAction",
    "NotificationType",
    "NotificationStatus",
    "NotificationChannel",
    "PartnerType",
]
