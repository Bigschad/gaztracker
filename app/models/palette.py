"""
Palette Model

Defines the Palette model for tracking gas bottle pallets.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, Float, ForeignKey, Index, Integer, Date, Boolean, Table, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


# Association table for many-to-many relationship between Palette and LivraisonDetail
livraison_palettes = Table(
    "livraison_palettes",
    Base.metadata,
    Column("livraison_detail_id", UUID(as_uuid=True), ForeignKey("livraisons_details.id", ondelete="CASCADE"), primary_key=True),
    Column("palette_id", UUID(as_uuid=True), ForeignKey("palettes.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Index("ix_livraison_palettes_livraison", "livraison_detail_id"),
    Index("ix_livraison_palettes_palette", "palette_id"),
)


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
    - AU_CENTRE: Palette at filling center (PLEINE or VIDE)
    - EN_CHARGEMENT: Being loaded
    - EN_ROUTE_LIVRAISON: In transit for delivery (PLEINE)
    - AU_DEPOT: At depot (PLEINE or VIDE)
    - EN_ROUTE_RETOUR: In transit returning to center (VIDE)
    - EN_CONTROLE: Under quality control
    - VALIDEE: Validated
    - OUT: Out of service/system
    """
    CREATION = "CREATION"
    AU_CENTRE = "AU_CENTRE"
    EN_CHARGEMENT = "EN_CHARGEMENT"
    EN_ROUTE_LIVRAISON = "EN_ROUTE_LIVRAISON"
    AU_DEPOT = "AU_DEPOT"
    EN_ROUTE_RETOUR = "EN_ROUTE_RETOUR"
    EN_CONTROLE = "EN_CONTROLE"
    VALIDEE = "VALIDEE"
    OUT = "OUT"


class PaletteCondition(str, enum.Enum):
    """
    Condition/State of a palette.

    - NEUVE: New palette (never used)
    - RECONDITIONNEE: Refurbished/reconditioned palette
    """
    NEUVE = "NEUVE"
    RECONDITIONNEE = "RECONDITIONNEE"


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

    # Condition (Neuve ou Reconditionnée)
    condition = Column(
        SQLEnum(PaletteCondition, name="palette_condition", create_type=True),
        nullable=True,
        default=PaletteCondition.NEUVE,
        index=True,
        comment="Condition de la palette (NEUVE ou RECONDITIONNEE)"
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

    # Current Location
    current_partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID du partenaire (grossiste) chez qui se trouve actuellement la palette"
    )
    
    current_depot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID du dépôt où se trouve actuellement la palette"
    )
    
    current_centre_remplisseur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("centres_remplisseurs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID du centre remplisseur où se trouve actuellement la palette"
    )

    status = Column(
        SQLEnum(PaletteStatus, name="palette_status", create_type=True),
        nullable=False,
        default=PaletteStatus.CREATION,
        index=True,
        comment="Current status in workflow"
    )
    
    # État de la palette (PLEINE / VIDE)
    is_full = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="True if palette is full, False if empty"
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

    # Current workflow documents
    bon_enlevement_actuel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_enlevement.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Current bon d'enlèvement if in delivery transit"
    )
    
    bon_retour_actuel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_reception_retour.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Current bon de réception retour if in return transit"
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

    current_partner = relationship(
        "Partner",
        foreign_keys=[current_partner_id]
    )
    
    current_depot = relationship(
        "Depot",
        foreign_keys=[current_depot_id]
    )
    
    current_centre_remplisseur = relationship(
        "CentreRemplisseur",
        foreign_keys=[current_centre_remplisseur_id]
    )
    
    bon_enlevement_actuel = relationship(
        "BonEnlevement",
        back_populates="palettes",
        foreign_keys=[bon_enlevement_actuel_id]
    )
    
    bon_retour_actuel = relationship(
        "BonReceptionRetour",
        back_populates="palettes_retournees",
        foreign_keys=[bon_retour_actuel_id]
    )
    
    livraisons = relationship(
        "LivraisonDetail",
        secondary=livraison_palettes,
        back_populates="palettes_livrees"
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
        Index("ix_palettes_bon_enlevement", "bon_enlevement_actuel_id"),
        Index("ix_palettes_bon_retour", "bon_retour_actuel_id"),
        Index("ix_palettes_depot", "current_depot_id"),
        Index("ix_palettes_centre", "current_centre_remplisseur_id"),
        Index("ix_palettes_full_status", "is_full", "status"),
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
        return self.status in [PaletteStatus.EN_ROUTE_LIVRAISON, PaletteStatus.EN_ROUTE_RETOUR]

    def is_at_center(self) -> bool:
        """Check if palette is at filling center."""
        return self.status == PaletteStatus.AU_CENTRE

    def is_at_depot(self) -> bool:
        """Check if palette is at depot."""
        return self.status == PaletteStatus.AU_DEPOT

    def can_be_assigned_for_delivery(self) -> bool:
        """Check if palette can be assigned to a bon d'enlèvement."""
        # Allow palettes in CREATION or AU_CENTRE status if they are full
        # A newly created palette at a centre can be assigned immediately
        return self.is_full and self.status in [PaletteStatus.CREATION, PaletteStatus.AU_CENTRE]

    def can_be_returned(self) -> bool:
        """Check if palette can be returned to center."""
        return self.status == PaletteStatus.AU_DEPOT and not self.is_full

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
