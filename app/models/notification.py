"""
Notification Model

Defines the Notification model for tracking system notifications.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class NotificationType(str, enum.Enum):
    """
    Types of notifications.

    - ALERTE_RETARD: Delivery delay alert
    - ANOMALIE_RFID: RFID anomaly/issue
    - DIVERGENCE_RECEPTION: Reception discrepancy
    - CONFIRMATION_LIVRAISON: Delivery confirmation
    - EXPEDITION_CREEE: New expedition created
    - EXPEDITION_DEPART: Expedition departed
    - EXPEDITION_ARRIVEE: Expedition arrived
    - PROBLEME_EXPEDITION: Expedition problem
    - VALIDATION_REQUISE: Validation required
    - RETOUR_PALETTE: Palette return notification
    """
    ALERTE_RETARD = "ALERTE_RETARD"
    ANOMALIE_RFID = "ANOMALIE_RFID"
    DIVERGENCE_RECEPTION = "DIVERGENCE_RECEPTION"
    CONFIRMATION_LIVRAISON = "CONFIRMATION_LIVRAISON"
    EXPEDITION_CREEE = "EXPEDITION_CREEE"
    EXPEDITION_DEPART = "EXPEDITION_DEPART"
    EXPEDITION_ARRIVEE = "EXPEDITION_ARRIVEE"
    PROBLEME_EXPEDITION = "PROBLEME_EXPEDITION"
    VALIDATION_REQUISE = "VALIDATION_REQUISE"
    RETOUR_PALETTE = "RETOUR_PALETTE"


class NotificationStatus(str, enum.Enum):
    """
    Status of notification delivery.

    - PENDING: Waiting to be sent
    - SENT: Successfully sent
    - FAILED: Failed to send
    - RETRYING: Retrying after failure
    """
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class NotificationChannel(str, enum.Enum):
    """
    Notification delivery channels.

    - EMAIL: Email notification
    - SMS: SMS notification
    - BOTH: Both email and SMS
    """
    EMAIL = "EMAIL"
    SMS = "SMS"
    BOTH = "BOTH"


class Notification(Base, TimestampMixin):
    """
    Notification model for tracking system notifications.

    Attributes:
        id: Unique notification identifier (UUID)
        type: Type of notification
        status: Delivery status
        channel: Delivery channel (email/SMS)
        recipient_email: Recipient email address
        recipient_phone: Recipient phone number
        subject: Notification subject/title
        message: Notification message content
        expedition_id: Related expedition (optional)
        palette_id: Related palette (optional)
        sent_at: When notification was sent
        error_message: Error message if failed
        retry_count: Number of retry attempts
        created_at: Timestamp when notification was created
        updated_at: Timestamp when notification was last updated
    """

    __tablename__ = "notifications"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique notification identifier"
    )

    # Notification Type & Status
    type = Column(
        SQLEnum(NotificationType, name="notification_type", create_type=True),
        nullable=False,
        index=True,
        comment="Type of notification"
    )

    status = Column(
        SQLEnum(NotificationStatus, name="notification_status", create_type=True),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
        comment="Delivery status"
    )

    channel = Column(
        SQLEnum(NotificationChannel, name="notification_channel", create_type=True),
        nullable=False,
        default=NotificationChannel.EMAIL,
        comment="Delivery channel"
    )

    # Recipient Information
    recipient_email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Recipient email address"
    )

    recipient_phone = Column(
        String(20),
        nullable=True,
        comment="Recipient phone number"
    )

    # Message Content
    subject = Column(
        String(255),
        nullable=True,
        comment="Notification subject/title"
    )

    message = Column(
        Text,
        nullable=False,
        comment="Notification message content"
    )

    # Foreign Keys
    expedition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expeditions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Related expedition (optional)"
    )

    palette_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palettes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Related palette (optional)"
    )

    # Delivery Information
    sent_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="When notification was sent"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )

    retry_count = Column(
        String(10),
        default="0",
        nullable=False,
        comment="Number of retry attempts"
    )

    # Relationships
    expedition = relationship(
        "Expedition",
        back_populates="notifications"
    )

    palette = relationship(
        "Palette",
        back_populates="notifications"
    )

    # Indexes
    __table_args__ = (
        Index("ix_notifications_status_created", "status", "created_at"),
        Index("ix_notifications_type_status", "type", "status"),
        Index("ix_notifications_recipient", "recipient_email", "status"),
    )

    def __repr__(self) -> str:
        """String representation of Notification."""
        return f"<Notification(id={self.id}, type={self.type}, status={self.status})>"

    def mark_as_sent(self) -> None:
        """Mark notification as successfully sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
        self.error_message = None

    def mark_as_failed(self, error: str) -> None:
        """
        Mark notification as failed.

        Args:
            error: Error message
        """
        self.status = NotificationStatus.FAILED
        self.error_message = error

    def increment_retry(self) -> None:
        """Increment retry count and set status to retrying."""
        self.retry_count = str(int(self.retry_count) + 1)
        self.status = NotificationStatus.RETRYING

    def should_retry(self, max_retries: int = 3) -> bool:
        """
        Check if notification should be retried.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if should retry
        """
        return (
            self.status in [NotificationStatus.FAILED, NotificationStatus.RETRYING] and
            int(self.retry_count) < max_retries
        )
