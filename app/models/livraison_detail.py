"""
Livraison Detail Model

Defines the LivraisonDetail model for multi-depot delivery details.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class LivraisonStatus(str, enum.Enum):
    """
    Status of a delivery.
    
    - EN_ATTENTE: Waiting
    - EN_COURS: In progress
    - LIVREE: Delivered
    - PROBLEME: Problem
    - ANNULEE: Cancelled
    """
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    LIVREE = "LIVREE"
    PROBLEME = "PROBLEME"
    ANNULEE = "ANNULEE"


class LivraisonDetail(Base, TimestampMixin):
    """
    Livraison Detail model for delivery step details.
    
    Used when truck makes a tour of deliveries (multi-depot).
    
    Attributes:
        id: Unique livraison detail identifier (UUID)
        bon_enlevement_id: FK to bons_enlevement
        ordre_livraison: Order in tour (1, 2, 3...)
        depot_id: FK to depots
        revendeur_id: FK to partners (if revendeur, else NULL for grossiste)
        date_arrivee: Arrival date
        date_depart: Departure date
        status: Current status
        recepteur_nom: Receiver name
        recepteur_signature: Receiver signature (Base64 or path)
        observations: Observations
        problemes: Problems description
        latitude_arrivee: GPS latitude at arrival
        longitude_arrivee: GPS longitude at arrival
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "livraisons_details"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique livraison detail identifier"
    )
    
    # Foreign Keys
    bon_enlevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_enlevement.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to bons_enlevement"
    )
    
    ordre_livraison = Column(
        Integer,
        nullable=False,
        comment="Order in tour (1, 2, 3...)"
    )
    
    # Destination
    depot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to depots"
    )
    
    revendeur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to partners (if revendeur, else NULL for grossiste)"
    )
    
    # Dates
    date_arrivee = Column(
        DateTime,
        nullable=True,
        comment="Arrival date"
    )
    
    date_depart = Column(
        DateTime,
        nullable=True,
        comment="Departure date"
    )
    
    # Status
    status = Column(
        SQLEnum(LivraisonStatus, name="livraison_status", create_type=True),
        nullable=False,
        default=LivraisonStatus.EN_ATTENTE,
        index=True,
        comment="Current status"
    )
    
    # Reception
    recepteur_nom = Column(
        String(255),
        nullable=True,
        comment="Receiver name"
    )
    
    recepteur_signature = Column(
        String(500),
        nullable=True,
        comment="Receiver signature (Base64 or path)"
    )
    
    observations = Column(
        String(1000),
        nullable=True,
        comment="Observations"
    )
    
    problemes = Column(
        String(1000),
        nullable=True,
        comment="Problems description"
    )
    
    # GPS
    latitude_arrivee = Column(
        Float,
        nullable=True,
        comment="GPS latitude at arrival"
    )
    
    longitude_arrivee = Column(
        Float,
        nullable=True,
        comment="GPS longitude at arrival"
    )
    
    # Relationships
    bon_enlevement = relationship(
        "BonEnlevement",
        back_populates="livraisons"
    )
    
    depot = relationship(
        "Depot",
        back_populates="livraisons_arrivees"
    )
    
    revendeur = relationship(
        "Partner",
        back_populates="livraisons_details",
        foreign_keys=[revendeur_id]
    )
    
    # Many-to-Many with Palette via association table
    palettes_livrees = relationship(
        "Palette",
        secondary="livraison_palettes",
        back_populates="livraisons"
    )
    
    collectes_vides = relationship(
        "CollecteVide",
        back_populates="livraison_detail",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    movements = relationship(
        "PaletteMovement",
        back_populates="livraison_detail",
        foreign_keys="PaletteMovement.livraison_detail_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_livraisons_bon", "bon_enlevement_id", "ordre_livraison"),
        Index("ix_livraisons_status", "status"),
        Index("ix_livraisons_depot", "depot_id"),
    )
    
    def __repr__(self) -> str:
        """String representation of LivraisonDetail."""
        return f"<LivraisonDetail(id={self.id}, ordre={self.ordre_livraison}, status={self.status})>"
    
    def is_completed(self) -> bool:
        """Check if livraison is completed."""
        return self.status in [LivraisonStatus.LIVREE, LivraisonStatus.ANNULEE]
    
    @property
    def has_location(self) -> bool:
        """Check if livraison has GPS coordinates."""
        return self.latitude_arrivee is not None and self.longitude_arrivee is not None

