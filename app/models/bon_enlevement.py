"""
Bon d'Enl

èvement Model

Defines the BonEnlevement model for delivery notes (outbound).
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class BonEnlevementStatus(str, enum.Enum):
    """
    Status of a bon d'enlèvement in the delivery workflow.
    
    - CREATION: Being created
    - VALIDE: Validated by centre
    - EN_CHARGEMENT: Loading in progress
    - EN_ROUTE: In transit
    - EN_LIVRAISON: Deliveries in progress (multi-depot)
    - TERMINE: All deliveries completed
    - ANNULE: Cancelled
    """
    CREATION = "CREATION"
    VALIDE = "VALIDE"
    EN_CHARGEMENT = "EN_CHARGEMENT"
    EN_ROUTE = "EN_ROUTE"
    EN_LIVRAISON = "EN_LIVRAISON"
    TERMINE = "TERMINE"
    ANNULE = "ANNULE"


class BonEnlevement(Base, TimestampMixin):
    """
    Bon d'Enlèvement model for outbound delivery notes.
    
    Journey: Centre Remplisseur → Depot(s)
    Content: FULL palettes (delivery) + EMPTY bottles collection
    
    Attributes:
        id: Unique bon d'enlèvement identifier (UUID)
        numero_bon: Unique bon number (e.g., "00000201/08")
        reference: Internal reference
        centre_remplisseur_id: FK to centres_remplisseurs
        grossiste_id: FK to partners (commissioning grossiste)
        depot_principal_id: FK to depots (grossiste's final depot)
        vehicule_immatriculation: Vehicle registration
        chauffeur_nom: Driver name
        chauffeur_societe: Driver company
        chauffeur_phone: Driver phone
        date_creation: Creation date
        date_validation: Validation date by centre
        date_chargement: Loading start date
        date_depart: Departure date from centre
        date_arrivee_finale: Arrival date at main depot
        status: Current status
        observations: Observations
        instructions_livraison: Delivery instructions
        validateur_centre_id: FK to users (who validated at centre)
        recepteur_final_id: FK to users (who received at main depot)
        otp_code: OTP code for security
        otp_expiry: OTP expiration time
        palette_count: Number of palettes in bon
        livraison_count: Number of deliveries
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "bons_enlevement"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique bon d'enlèvement identifier"
    )
    
    # Numbers
    numero_bon = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique bon number"
    )
    
    reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Internal reference"
    )
    
    # Origin
    centre_remplisseur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("centres_remplisseurs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to centres_remplisseurs"
    )
    
    # Destination
    grossiste_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to partners (commissioning grossiste)"
    )
    
    depot_principal_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to depots (grossiste's final depot)"
    )
    
    # Transport
    vehicule_immatriculation = Column(
        String(50),
        nullable=True,
        comment="Vehicle registration"
    )
    
    chauffeur_nom = Column(
        String(255),
        nullable=True,
        comment="Driver name"
    )
    
    chauffeur_societe = Column(
        String(255),
        nullable=True,
        comment="Driver company"
    )
    
    chauffeur_phone = Column(
        String(20),
        nullable=True,
        comment="Driver phone"
    )
    
    # Dates
    date_creation = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Creation date"
    )
    
    date_validation = Column(
        DateTime,
        nullable=True,
        comment="Validation date by centre"
    )
    
    date_chargement = Column(
        DateTime,
        nullable=True,
        comment="Loading start date"
    )
    
    date_depart = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Departure date from centre"
    )
    
    date_arrivee_finale = Column(
        DateTime,
        nullable=True,
        comment="Arrival date at main depot"
    )
    
    # Status
    status = Column(
        SQLEnum(BonEnlevementStatus, name="bon_enlevement_status", create_type=True),
        nullable=False,
        default=BonEnlevementStatus.CREATION,
        index=True,
        comment="Current status"
    )
    
    # Information
    observations = Column(
        String(1000),
        nullable=True,
        comment="Observations"
    )
    
    instructions_livraison = Column(
        String(1000),
        nullable=True,
        comment="Delivery instructions"
    )
    
    # Validation
    validateur_centre_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to users (who validated at centre)"
    )
    
    recepteur_final_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to users (who received at main depot)"
    )
    
    # OTP for security
    otp_code = Column(
        String(10),
        nullable=True,
        comment="OTP code for security"
    )
    
    otp_expiry = Column(
        DateTime,
        nullable=True,
        comment="OTP expiration time"
    )
    
    # Counters
    palette_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of palettes in bon"
    )
    
    livraison_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of deliveries"
    )
    
    # Relationships
    centre_remplisseur = relationship(
        "CentreRemplisseur",
        back_populates="bons_enlevement"
    )
    
    grossiste = relationship(
        "Partner",
        back_populates="bons_enlevement",
        foreign_keys=[grossiste_id]
    )
    
    depot_principal = relationship(
        "Depot",
        back_populates="bons_enlevement"
    )
    
    validateur_centre = relationship(
        "User",
        foreign_keys=[validateur_centre_id]
    )
    
    recepteur_final = relationship(
        "User",
        foreign_keys=[recepteur_final_id]
    )
    
    palettes = relationship(
        "Palette",
        back_populates="bon_enlevement_actuel",
        foreign_keys="Palette.bon_enlevement_actuel_id",
        lazy="dynamic"
    )
    
    livraisons = relationship(
        "LivraisonDetail",
        back_populates="bon_enlevement",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    collectes_vides = relationship(
        "CollecteVide",
        back_populates="bon_enlevement",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    movements = relationship(
        "PaletteMovement",
        back_populates="bon_enlevement",
        foreign_keys="PaletteMovement.bon_enlevement_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_bons_enl_numero_status", "numero_bon", "status"),
        Index("ix_bons_enl_centre", "centre_remplisseur_id", "status"),
        Index("ix_bons_enl_grossiste", "grossiste_id", "status"),
        Index("ix_bons_enl_dates", "date_creation", "date_depart"),
    )
    
    def __repr__(self) -> str:
        """String representation of BonEnlevement."""
        return f"<BonEnlevement(id={self.id}, numero={self.numero_bon}, status={self.status})>"
    
    def is_in_transit(self) -> bool:
        """Check if bon is in transit."""
        return self.status in [BonEnlevementStatus.EN_ROUTE, BonEnlevementStatus.EN_LIVRAISON]
    
    def is_completed(self) -> bool:
        """Check if bon is completed."""
        return self.status in [BonEnlevementStatus.TERMINE, BonEnlevementStatus.ANNULE]
    
    def can_be_modified(self) -> bool:
        """Check if bon can still be modified."""
        return self.status in [BonEnlevementStatus.CREATION, BonEnlevementStatus.VALIDE]
    
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
        
        return (
            self.otp_code == otp and
            datetime.utcnow() < self.otp_expiry
        )

