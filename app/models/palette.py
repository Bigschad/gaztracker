"""
Palette Model

Defines the Palette model for tracking gas bottle pallets.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, Float, ForeignKey, Index, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class PaletteType(str, enum.Enum):
    """
    Types of gas bottle pallets.

    - B6: 6kg gas bottles
    - B12: 12kg gas bottles
    - B28: 28kg gas bottles
    """
    B6 = "B6"
    B12 = "B12"
    B28 = "B28"


class PaletteStatus(str, enum.Enum):
    """
    Status of a palette in the tracking workflow.

    - CREATION: Palette just created
    - EN_STOCK: Palette in factory stock
    - EN_ROUTE: Palette in transit
    - EN_RECEPTION: Palette arrived at destination, awaiting validation
    - LIVREE: Palette delivered and validated
    - RETOURNEE: Palette returned to factory
    - OUT: Palette out of service/system
    """
    CREATION = "CREATION"
    EN_STOCK = "EN_STOCK"
    EN_ROUTE = "EN_ROUTE"
    EN_RECEPTION = "EN_RECEPTION"
    LIVREE = "LIVREE"
    RETOURNEE = "RETOURNEE"
    OUT = "OUT"


class Palette(Base, TimestampMixin):
    """
    Palette model for tracking gas bottle pallets.

    Attributes:
        id: Unique palette identifier (UUID)
        rfid_tag: Unique RFID tag identifier
        type: Type of gas bottles (B6, B12, B28)
        status: Current status in workflow
        location_latitude: Current GPS latitude (optional)
        location_longitude: Current GPS longitude (optional)
        location_address: Current address (optional)
        notes: Additional notes
        created_by_id: User who created the palette
        current_expedition_id: Current expedition (if in transit)
        created_at: Timestamp when palette was created
        updated_at: Timestamp when palette was last updated
    """

    __tablename__ = "palettes"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique palette identifier"
    )

    # Serial Number (human-readable identifier, auto-generated)
    serial_number = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Human-readable serial number (e.g., PAL-2025-00001)"
    )

    # Reference Code (code de référence, saisie manuelle)
    reference_code = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Code de référence personnalisé (saisie manuelle)"
    )

    # RFID Tag - Relation avec le modèle RFIDTag
    rfid_tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rfid_tags.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        comment="ID du tag RFID assigné à cette palette"
    )

    # Palette Information
    type = Column(
        SQLEnum(PaletteType, name="palette_type", create_type=True),
        nullable=False,
        index=True,
        comment="Type of gas bottles (B6, B12, B28)"
    )

    # Capacity (capacité - nombre de bouteilles possible)
    capacity = Column(
        Integer,
        nullable=True,
        comment="Capacité en nombre de bouteilles possibles"
    )

    # Manufacturing Date (date de fabrication)
    manufacturing_date = Column(
        Date,
        nullable=True,
        comment="Date de fabrication de la palette"
    )

    # Current Partner/Location (grossiste actuel)
    current_partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID du partenaire (grossiste) chez qui se trouve actuellement la palette"
    )

    status = Column(
        SQLEnum(PaletteStatus, name="palette_status", create_type=True),
        nullable=False,
        default=PaletteStatus.CREATION,
        index=True,
        comment="Current status in workflow"
    )

    # Geolocation
    location_latitude = Column(
        Float,
        nullable=True,
        comment="Current GPS latitude"
    )

    location_longitude = Column(
        Float,
        nullable=True,
        comment="Current GPS longitude"
    )

    location_address = Column(
        String(500),
        nullable=True,
        comment="Current address"
    )

    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes about palette"
    )

    # Foreign Keys
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the palette"
    )

    current_expedition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expeditions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Current expedition if in transit"
    )

    # Relationships
    rfid_tag = relationship(
        "RFIDTag",
        back_populates="palette",
        foreign_keys=[rfid_tag_id],
        uselist=False
    )

    created_by = relationship(
        "User",
        back_populates="created_palettes",
        foreign_keys=[created_by_id]
    )

    current_expedition = relationship(
        "Expedition",
        back_populates="palettes",
        foreign_keys=[current_expedition_id]
    )

    current_partner = relationship(
        "Partner",
        foreign_keys=[current_partner_id]
    )

    movements = relationship(
        "PaletteMovement",
        back_populates="palette",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="desc(PaletteMovement.timestamp)"
    )

    notifications = relationship(
        "Notification",
        back_populates="palette",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_palettes_rfid_status", "rfid_tag_id", "status"),
        Index("ix_palettes_type_status", "type", "status"),
        Index("ix_palettes_expedition", "current_expedition_id"),
    )

    def __repr__(self) -> str:
        """String representation of Palette."""
        return f"<Palette(id={self.id}, rfid={self.rfid_tag}, type={self.type}, status={self.status})>"

    @property
    def has_location(self) -> bool:
        """Check if palette has geolocation data."""
        return self.location_latitude is not None and self.location_longitude is not None

    def is_in_transit(self) -> bool:
        """Check if palette is currently in transit."""
        return self.status == PaletteStatus.EN_ROUTE

    def is_delivered(self) -> bool:
        """Check if palette has been delivered."""
        return self.status == PaletteStatus.LIVREE

    def is_available(self) -> bool:
        """Check if palette is available (in stock)."""
        return self.status == PaletteStatus.EN_STOCK

    def can_be_assigned(self) -> bool:
        """Check if palette can be assigned to an expedition."""
        return self.status in [PaletteStatus.CREATION, PaletteStatus.EN_STOCK, PaletteStatus.RETOURNEE]

    def update_location(self, latitude: float, longitude: float, address: str = None) -> None:
        """
        Update palette location.

        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            address: Physical address (optional)
        """
        self.location_latitude = latitude
        self.location_longitude = longitude
        if address:
            self.location_address = address
