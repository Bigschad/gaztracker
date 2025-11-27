"""
Collecte Vide Model

Defines the CollecteVide model for empty bottle collection.
"""

from sqlalchemy import Column, Enum as SQLEnum, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin
from app.models.palette import PaletteType


class CollecteVide(Base, TimestampMixin):
    """
    Collecte Vide model for empty bottle collection.
    
    Collection of empty bottles during a delivery.
    
    Attributes:
        id: Unique collecte vide identifier (UUID)
        bon_enlevement_id: FK to bons_enlevement
        livraison_detail_id: FK to livraisons_details (if multi-depot)
        depot_id: FK to depots (where collection occurred)
        type_bouteille: Bottle type (B6, B12, B28)
        quantite_bouteilles_vides: Number of empty bottles
        quantite_palettes_vides: Number of empty palette structures
        date_collecte: Collection date
        collecteur_nom: Collector name (often driver)
        observations: Observations
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "collectes_vides"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique collecte vide identifier"
    )
    
    # Foreign Keys
    bon_enlevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_enlevement.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to bons_enlevement"
    )
    
    livraison_detail_id = Column(
        UUID(as_uuid=True),
        ForeignKey("livraisons_details.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to livraisons_details (if multi-depot)"
    )
    
    depot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to depots (where collection occurred)"
    )
    
    # Collection Details
    type_bouteille = Column(
        SQLEnum(PaletteType, name="palette_type", create_type=False),
        nullable=False,
        comment="Bottle type (B6, B12, B28)"
    )
    
    quantite_bouteilles_vides = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of empty bottles"
    )
    
    quantite_palettes_vides = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of empty palette structures"
    )
    
    # Date
    date_collecte = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Collection date"
    )
    
    # Collector
    collecteur_nom = Column(
        String(255),
        nullable=True,
        comment="Collector name (often driver)"
    )
    
    # Additional Information
    observations = Column(
        String(1000),
        nullable=True,
        comment="Observations"
    )
    
    # Relationships
    bon_enlevement = relationship(
        "BonEnlevement",
        back_populates="collectes_vides"
    )
    
    livraison_detail = relationship(
        "LivraisonDetail",
        back_populates="collectes_vides"
    )
    
    depot = relationship(
        "Depot",
        back_populates="collectes_vides"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_collectes_bon", "bon_enlevement_id"),
        Index("ix_collectes_livraison", "livraison_detail_id"),
        Index("ix_collectes_depot", "depot_id"),
        Index("ix_collectes_date", "date_collecte"),
    )
    
    def __repr__(self) -> str:
        """String representation of CollecteVide."""
        return f"<CollecteVide(id={self.id}, type={self.type_bouteille}, qty={self.quantite_bouteilles_vides})>"
    
    @property
    def total_items(self) -> int:
        """Get total items collected."""
        return self.quantite_bouteilles_vides + self.quantite_palettes_vides

