"""
Expedition Model

Defines the Expedition model for tracking palette deliveries.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class ExpeditionStatus(str, enum.Enum):
    """
    Status of an expedition in the delivery workflow.

    - CREATION: Expedition being created
    - EN_ATTENTE: Awaiting approval/validation
    - CREEE: Created and approved, ready for departure
    - EN_TRANSIT: In transit to destination
    - ARRIVEE: Arrived at destination, pending reception
    - LIVREE: Delivered and validated by recipient
    - PROBLEME: Issue/problem with delivery
    - ANNULEE: Expedition cancelled
    """
    CREATION = "CREATION"
    EN_ATTENTE = "EN_ATTENTE"
    CREEE = "CREEE"
    EN_TRANSIT = "EN_TRANSIT"
    ARRIVEE = "ARRIVEE"
    LIVREE = "LIVREE"
    PROBLEME = "PROBLEME"
    ANNULEE = "ANNULEE"


class Expedition(Base, TimestampMixin):
    """
    Expedition model for tracking palette deliveries.

    Attributes:
        id: Unique expedition identifier (UUID)
        reference_number: Unique reference number
        status: Current status in workflow
        date_creation: Date expedition was created
        date_departure: Date expedition departed
        eta: Estimated time of arrival
        date_arrival: Actual arrival date
        date_delivery: Date delivery was completed
        transporter: Name of transport company/driver
        vehicle_info: Vehicle information (plate, type, etc.)
        destination_address: Delivery address
        destination_contact: Contact person at destination
        destination_phone: Contact phone at destination
        notes: Additional notes
        problem_description: Description if status is PROBLEME
        otp_code: One-time password for delivery validation
        otp_expiry: OTP expiration time
        palette_count: Number of palettes in expedition
        created_by_id: User who created the expedition
        validated_by_id: User who validated the expedition
        created_at: Timestamp when expedition was created
        updated_at: Timestamp when expedition was last updated
    """

    __tablename__ = "expeditions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique expedition identifier"
    )

    # Reference
    reference_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique reference number"
    )

    # Status
    status = Column(
        SQLEnum(ExpeditionStatus, name="expedition_status", create_type=True),
        nullable=False,
        default=ExpeditionStatus.CREATION,
        index=True,
        comment="Current status in workflow"
    )

    # Dates
    date_creation = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Date expedition was created"
    )

    date_departure = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Date expedition departed"
    )

    eta = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Estimated time of arrival"
    )

    date_arrival = Column(
        DateTime,
        nullable=True,
        comment="Actual arrival date"
    )

    date_delivery = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Date delivery was completed"
    )

    # Transport Information
    transporter = Column(
        String(255),
        nullable=True,
        comment="Name of transport company/driver"
    )

    vehicle_info = Column(
        String(255),
        nullable=True,
        comment="Vehicle information (plate, type, etc.)"
    )

    # Destination Information
    destination_address = Column(
        String(500),
        nullable=False,
        comment="Delivery address"
    )

    destination_contact = Column(
        String(255),
        nullable=True,
        comment="Contact person at destination"
    )

    destination_phone = Column(
        String(20),
        nullable=True,
        comment="Contact phone at destination"
    )

    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )

    problem_description = Column(
        String(1000),
        nullable=True,
        comment="Description if status is PROBLEME"
    )

    # OTP for delivery validation
    otp_code = Column(
        String(10),
        nullable=True,
        comment="One-time password for delivery validation"
    )

    otp_expiry = Column(
        DateTime,
        nullable=True,
        comment="OTP expiration time"
    )

    # Palette Count
    palette_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of palettes in expedition"
    )

    # Foreign Keys
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the expedition"
    )

    validated_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who validated the expedition"
    )

    # Relationships
    created_by = relationship(
        "User",
        back_populates="created_expeditions",
        foreign_keys=[created_by_id]
    )

    validated_by = relationship(
        "User",
        back_populates="validated_expeditions",
        foreign_keys=[validated_by_id]
    )

    palettes = relationship(
        "Palette",
        back_populates="current_expedition",
        foreign_keys="Palette.current_expedition_id",
        lazy="dynamic"
    )

    movements = relationship(
        "PaletteMovement",
        back_populates="expedition",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    notifications = relationship(
        "Notification",
        back_populates="expedition",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_expeditions_ref_status", "reference_number", "status"),
        Index("ix_expeditions_dates", "date_departure", "eta"),
        Index("ix_expeditions_status_dates", "status", "date_creation"),
    )

    def __repr__(self) -> str:
        """String representation of Expedition."""
        return f"<Expedition(id={self.id}, ref={self.reference_number}, status={self.status})>"

    def is_in_transit(self) -> bool:
        """Check if expedition is in transit."""
        return self.status == ExpeditionStatus.EN_TRANSIT

    def is_delivered(self) -> bool:
        """Check if expedition is delivered."""
        return self.status == ExpeditionStatus.LIVREE

    def is_completed(self) -> bool:
        """Check if expedition is completed (delivered or cancelled)."""
        return self.status in [ExpeditionStatus.LIVREE, ExpeditionStatus.ANNULEE]

    def can_be_modified(self) -> bool:
        """Check if expedition can still be modified."""
        return self.status in [ExpeditionStatus.CREATION, ExpeditionStatus.EN_ATTENTE]

    def can_add_palettes(self) -> bool:
        """Check if palettes can still be added."""
        return self.status in [ExpeditionStatus.CREATION, ExpeditionStatus.EN_ATTENTE, ExpeditionStatus.CREEE]

    def is_delayed(self) -> bool:
        """
        Check if expedition is delayed.

        Returns:
            bool: True if current time is past ETA and not delivered
        """
        if not self.eta or self.is_delivered():
            return False
        return datetime.utcnow() > self.eta

    def validate_otp(self, otp: str) -> bool:
        """
        Validate OTP code.

        Args:
            otp: OTP code to validate

        Returns:
            bool: True if OTP is valid and not expired
        """
        if not self.otp_code or not self.otp_expiry:
            return False

        # Check if OTP matches and not expired
        return (
            self.otp_code == otp and
            datetime.utcnow() < self.otp_expiry
        )
