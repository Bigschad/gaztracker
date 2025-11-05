"""
Palette Movement Model

Defines the PaletteMovement model for tracking palette history.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class MovementAction(str, enum.Enum):
    """
    Types of actions that can be performed on palettes.

    - CREATION: Palette created
    - SCANNING_DEPART: Scanned at departure
    - SCANNING_ARRIVEE: Scanned at arrival
    - VALIDATION_RECEPTION: Reception validated
    - UPDATE_LOCATION: Location updated
    - STATUS_CHANGE: Status changed
    - ASSIGNATION_EXPEDITION: Assigned to expedition
    - RETOUR_USINE: Returned to factory
    - MISE_HORS_SERVICE: Put out of service
    """
    CREATION = "CREATION"
    SCANNING_DEPART = "SCANNING_DEPART"
    SCANNING_ARRIVEE = "SCANNING_ARRIVEE"
    VALIDATION_RECEPTION = "VALIDATION_RECEPTION"
    UPDATE_LOCATION = "UPDATE_LOCATION"
    STATUS_CHANGE = "STATUS_CHANGE"
    ASSIGNATION_EXPEDITION = "ASSIGNATION_EXPEDITION"
    RETOUR_USINE = "RETOUR_USINE"
    MISE_HORS_SERVICE = "MISE_HORS_SERVICE"


class PaletteMovement(Base):
    """
    Palette movement model for tracking palette history and audit trail.

    Attributes:
        id: Unique movement identifier (UUID)
        palette_id: Related palette
        expedition_id: Related expedition (optional)
        user_id: User who performed the action
        action: Type of action performed
        status_before: Status before action
        status_after: Status after action
        location: Location where action was performed
        latitude: GPS latitude (optional)
        longitude: GPS longitude (optional)
        timestamp: When action was performed
        details: Additional details (JSON)
        notes: Additional notes
    """

    __tablename__ = "palette_movements"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique movement identifier"
    )

    # Foreign Keys
    palette_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palettes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Related palette"
    )

    expedition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expeditions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related expedition (optional)"
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )

    # Action Information
    action = Column(
        SQLEnum(MovementAction, name="movement_action", create_type=True),
        nullable=False,
        index=True,
        comment="Type of action performed"
    )

    status_before = Column(
        String(50),
        nullable=True,
        comment="Status before action"
    )

    status_after = Column(
        String(50),
        nullable=True,
        comment="Status after action"
    )

    # Location Information
    location = Column(
        String(500),
        nullable=True,
        comment="Location where action was performed"
    )

    latitude = Column(
        String(50),
        nullable=True,
        comment="GPS latitude"
    )

    longitude = Column(
        String(50),
        nullable=True,
        comment="GPS longitude"
    )

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When action was performed"
    )

    # Additional Information
    details = Column(
        JSON,
        nullable=True,
        comment="Additional details (JSON)"
    )

    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )

    # Relationships
    palette = relationship(
        "Palette",
        back_populates="movements"
    )

    expedition = relationship(
        "Expedition",
        back_populates="movements"
    )

    user = relationship(
        "User",
        back_populates="palette_movements"
    )

    # Indexes
    __table_args__ = (
        Index("ix_movements_palette_timestamp", "palette_id", "timestamp"),
        Index("ix_movements_expedition_timestamp", "expedition_id", "timestamp"),
        Index("ix_movements_action_timestamp", "action", "timestamp"),
    )

    def __repr__(self) -> str:
        """String representation of PaletteMovement."""
        return f"<PaletteMovement(id={self.id}, palette={self.palette_id}, action={self.action})>"

    @property
    def has_location(self) -> bool:
        """Check if movement has geolocation data."""
        return self.latitude is not None and self.longitude is not None
