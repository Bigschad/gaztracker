"""
Detail Retour Model

Defines the DetailRetour model for return detail items.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, ForeignKey, Index, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin
from app.models.palette import PaletteType


class DetailRetourType(str, enum.Enum):
    """
    Type of return detail.
    
    - PALETTE_VIDE: Empty palette structure
    - BOUTEILLE_VIDE: Empty bottle
    - CONSIGNE: Deposit
    """
    PALETTE_VIDE = "PALETTE_VIDE"
    BOUTEILLE_VIDE = "BOUTEILLE_VIDE"
    CONSIGNE = "CONSIGNE"


class DetailRetourEtat(str, enum.Enum):
    """
    State of returned item.
    
    - BON: Good condition
    - MOYEN: Average condition
    - MAUVAIS: Bad condition
    - REFUSE: Refused
    """
    BON = "BON"
    MOYEN = "MOYEN"
    MAUVAIS = "MAUVAIS"
    REFUSE = "REFUSE"


class DetailRetour(Base, TimestampMixin):
    """
    Detail Retour model for return item details.
    
    Tracks details of each item type in a return shipment.
    
    Attributes:
        id: Unique detail retour identifier (UUID)
        bon_reception_retour_id: FK to bons_reception_retour
        type_detail: Type of item (PALETTE_VIDE, BOUTEILLE_VIDE, CONSIGNE)
        type_bouteille: Bottle type (B6, B12, B28)
        quantite_prevue: Expected quantity
        quantite_recue: Received quantity
        quantite_acceptee: Accepted quantity
        quantite_refusee: Refused quantity
        etat: Condition state
        observations: Observations
        motif_refus: Refusal reason
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "details_retour"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique detail retour identifier"
    )
    
    # Foreign Keys
    bon_reception_retour_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_reception_retour.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to bons_reception_retour"
    )
    
    # Item Details
    type_detail = Column(
        SQLEnum(DetailRetourType, name="detail_retour_type", create_type=True),
        nullable=False,
        comment="Type of item"
    )
    
    type_bouteille = Column(
        SQLEnum(PaletteType, name="palette_type", create_type=False),
        nullable=True,
        comment="Bottle type (B6, B12, B28)"
    )
    
    # Quantities
    quantite_prevue = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Expected quantity"
    )
    
    quantite_recue = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Received quantity"
    )
    
    quantite_acceptee = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Accepted quantity"
    )
    
    quantite_refusee = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Refused quantity"
    )
    
    # Quality
    etat = Column(
        SQLEnum(DetailRetourEtat, name="detail_retour_etat", create_type=True),
        nullable=True,
        comment="Condition state"
    )
    
    observations = Column(
        String(1000),
        nullable=True,
        comment="Observations"
    )
    
    motif_refus = Column(
        String(500),
        nullable=True,
        comment="Refusal reason"
    )
    
    # Relationships
    bon_reception_retour = relationship(
        "BonReceptionRetour",
        back_populates="details_retour"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_details_retour_bon", "bon_reception_retour_id"),
        Index("ix_details_retour_type", "type_detail", "type_bouteille"),
    )
    
    def __repr__(self) -> str:
        """String representation of DetailRetour."""
        return f"<DetailRetour(id={self.id}, type={self.type_detail}, qty={self.quantite_recue})>"
    
    @property
    def ecart_quantite(self) -> int:
        """Calculate quantity difference."""
        return self.quantite_recue - self.quantite_prevue
    
    @property
    def taux_acceptation(self) -> float:
        """Calculate acceptance rate."""
        if self.quantite_recue == 0:
            return 0.0
        return (self.quantite_acceptee / self.quantite_recue) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if all received items are processed."""
        return self.quantite_recue == (self.quantite_acceptee + self.quantite_refusee)

