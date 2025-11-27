"""
Bon de Réception Retour Model

Defines the BonReceptionRetour model for return reception notes (inbound).
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class BonReceptionRetourStatus(str, enum.Enum):
    """
    Status of a bon de réception retour in the return workflow.
    
    - CREATION: Being created
    - EN_ROUTE: In transit
    - ARRIVE: Arrived
    - EN_CONTROLE: Quality control in progress
    - VALIDE: Validated
    - REFUSE: Refused
    """
    CREATION = "CREATION"
    EN_ROUTE = "EN_ROUTE"
    ARRIVE = "ARRIVE"
    EN_CONTROLE = "EN_CONTROLE"
    VALIDE = "VALIDE"
    REFUSE = "REFUSE"


class BonReceptionRetour(Base, TimestampMixin):
    """
    Bon de Réception Retour model for inbound return notes.
    
    Journey: Depot Grossiste → Centre Remplisseur
    Content: EMPTY palettes + Empty bottles
    
    Attributes:
        id: Unique bon reception retour identifier (UUID)
        numero_bl: BL number (e.g., "BL N°75 du 13.08.25")
        numero_reception: Reception number (e.g., "0001320/08 MB")
        grossiste_id: FK to partners
        depot_depart_id: FK to depots
        centre_remplisseur_id: FK to centres_remplisseurs
        vehicule_immatriculation: Vehicle registration
        transporteur_nom: Transporter name
        transporteur_societe: Transporter company
        date_creation: Creation date
        date_depart: Departure date
        date_arrivee: Arrival date
        date_controle: Quality control date
        date_validation: Validation date
        status: Current status
        controleur_id: FK to users (quality controller)
        magasinier_id: FK to users (warehouse keeper)
        observations: Observations
        manquants: Missing items description
        client_signature: Client signature
        magasinier_signature: Warehouse keeper signature
        controleur_signature: Quality controller signature
        palette_count: Number of palettes
        palette_acceptees: Number of accepted palettes
        palette_refusees: Number of refused palettes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "bons_reception_retour"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique bon reception retour identifier"
    )
    
    # Numbers
    numero_bl = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="BL number"
    )
    
    numero_reception = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Reception number"
    )
    
    # Origin
    grossiste_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to partners"
    )
    
    depot_depart_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to depots"
    )
    
    # Destination
    centre_remplisseur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("centres_remplisseurs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to centres_remplisseurs"
    )
    
    # Transport
    vehicule_immatriculation = Column(
        String(50),
        nullable=True,
        comment="Vehicle registration"
    )
    
    transporteur_nom = Column(
        String(255),
        nullable=True,
        comment="Transporter name"
    )
    
    transporteur_societe = Column(
        String(255),
        nullable=True,
        comment="Transporter company"
    )
    
    # Dates
    date_creation = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Creation date"
    )
    
    date_depart = Column(
        DateTime,
        nullable=True,
        comment="Departure date"
    )
    
    date_arrivee = Column(
        DateTime,
        nullable=True,
        comment="Arrival date"
    )
    
    date_controle = Column(
        DateTime,
        nullable=True,
        comment="Quality control date"
    )
    
    date_validation = Column(
        DateTime,
        nullable=True,
        comment="Validation date"
    )
    
    # Status
    status = Column(
        SQLEnum(BonReceptionRetourStatus, name="bon_reception_retour_status", create_type=True),
        nullable=False,
        default=BonReceptionRetourStatus.CREATION,
        index=True,
        comment="Current status"
    )
    
    # Quality Control
    controleur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to users (quality controller)"
    )
    
    magasinier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to users (warehouse keeper)"
    )
    
    observations = Column(
        String(1000),
        nullable=True,
        comment="Observations"
    )
    
    manquants = Column(
        String(1000),
        nullable=True,
        comment="Missing items description"
    )
    
    # Signatures
    client_signature = Column(
        String(500),
        nullable=True,
        comment="Client signature"
    )
    
    magasinier_signature = Column(
        String(500),
        nullable=True,
        comment="Warehouse keeper signature"
    )
    
    controleur_signature = Column(
        String(500),
        nullable=True,
        comment="Quality controller signature"
    )
    
    # Counters
    palette_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of palettes"
    )
    
    palette_acceptees = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of accepted palettes"
    )
    
    palette_refusees = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of refused palettes"
    )
    
    # Relationships
    grossiste = relationship(
        "Partner",
        back_populates="bons_reception_retour",
        foreign_keys=[grossiste_id]
    )
    
    depot_depart = relationship(
        "Depot",
        back_populates="bons_reception_retour_depart"
    )
    
    centre_remplisseur = relationship(
        "CentreRemplisseur",
        back_populates="bons_reception_retour"
    )
    
    controleur = relationship(
        "User",
        foreign_keys=[controleur_id]
    )
    
    magasinier = relationship(
        "User",
        foreign_keys=[magasinier_id]
    )
    
    palettes_retournees = relationship(
        "Palette",
        back_populates="bon_retour_actuel",
        foreign_keys="Palette.bon_retour_actuel_id",
        lazy="dynamic"
    )
    
    details_retour = relationship(
        "DetailRetour",
        back_populates="bon_reception_retour",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    movements = relationship(
        "PaletteMovement",
        back_populates="bon_reception_retour",
        foreign_keys="PaletteMovement.bon_reception_retour_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_bons_ret_numero_bl_status", "numero_bl", "status"),
        Index("ix_bons_ret_grossiste", "grossiste_id", "status"),
        Index("ix_bons_ret_centre", "centre_remplisseur_id", "status"),
        Index("ix_bons_ret_dates", "date_creation", "date_arrivee"),
    )
    
    def __repr__(self) -> str:
        """String representation of BonReceptionRetour."""
        return f"<BonReceptionRetour(id={self.id}, numero_bl={self.numero_bl}, status={self.status})>"
    
    def is_in_transit(self) -> bool:
        """Check if bon is in transit."""
        return self.status == BonReceptionRetourStatus.EN_ROUTE
    
    def is_completed(self) -> bool:
        """Check if bon is completed."""
        return self.status in [BonReceptionRetourStatus.VALIDE, BonReceptionRetourStatus.REFUSE]
    
    def can_be_modified(self) -> bool:
        """Check if bon can still be modified."""
        return self.status == BonReceptionRetourStatus.CREATION
    
    @property
    def taux_acceptation(self) -> float:
        """Calculate acceptance rate."""
        if self.palette_count == 0:
            return 0.0
        return (self.palette_acceptees / self.palette_count) * 100

