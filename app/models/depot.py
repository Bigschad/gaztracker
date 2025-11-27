"""
Depot Model

Defines the Depot model for storage locations.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Float, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin


class Depot(Base, TimestampMixin):
    """
    Depot model for storage locations.
    
    Storage point for a grossiste (wholesaler) or revendeur (reseller).
    
    Attributes:
        id: Unique depot identifier (UUID)
        name: Depot name
        code: Unique code
        partner_id: FK to partners (grossiste or revendeur)
        address: Address
        city: City
        postal_code: Postal code
        latitude: GPS latitude
        longitude: GPS longitude
        contact_name: Contact person name
        contact_phone: Contact person phone
        capacity_b28: Capacity for B28 palettes
        capacity_b12: Capacity for B12 palettes
        capacity_b6: Capacity for B6 palettes
        is_active: Whether the depot is active
        is_main_depot: Whether this is the main depot of the partner
        notes: Additional notes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "depots"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique depot identifier"
    )
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Depot name"
    )
    
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique code"
    )
    
    # Foreign Keys
    partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to partners (grossiste or revendeur)"
    )
    
    # Address Information
    address = Column(
        String(500),
        nullable=False,
        comment="Street address"
    )
    
    city = Column(
        String(100),
        nullable=False,
        comment="City"
    )
    
    postal_code = Column(
        String(20),
        nullable=True,
        comment="Postal code"
    )
    
    # GPS Coordinates
    latitude = Column(
        Float,
        nullable=True,
        comment="GPS latitude"
    )
    
    longitude = Column(
        Float,
        nullable=True,
        comment="GPS longitude"
    )
    
    # Contact Information
    contact_name = Column(
        String(255),
        nullable=True,
        comment="Contact person name"
    )
    
    contact_phone = Column(
        String(20),
        nullable=True,
        comment="Contact person phone"
    )
    
    # Capacity
    capacity_b28 = Column(
        Integer,
        nullable=True,
        comment="Capacity for B28 palettes"
    )
    
    capacity_b12 = Column(
        Integer,
        nullable=True,
        comment="Capacity for B12 palettes"
    )
    
    capacity_b6 = Column(
        Integer,
        nullable=True,
        comment="Capacity for B6 palettes"
    )
    
    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether depot is active"
    )
    
    is_main_depot = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this is the main depot of the partner"
    )
    
    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )
    
    # Relationships
    partner = relationship(
        "Partner",
        back_populates="depots"
    )
    
    bons_enlevement = relationship(
        "BonEnlevement",
        back_populates="depot_principal",
        foreign_keys="BonEnlevement.depot_principal_id",
        lazy="dynamic"
    )
    
    livraisons_arrivees = relationship(
        "LivraisonDetail",
        back_populates="depot",
        foreign_keys="LivraisonDetail.depot_id",
        lazy="dynamic"
    )
    
    collectes_vides = relationship(
        "CollecteVide",
        back_populates="depot",
        foreign_keys="CollecteVide.depot_id",
        lazy="dynamic"
    )
    
    bons_reception_retour_depart = relationship(
        "BonReceptionRetour",
        back_populates="depot_depart",
        foreign_keys="BonReceptionRetour.depot_depart_id",
        lazy="dynamic"
    )
    
    palettes = relationship(
        "Palette",
        back_populates="current_depot",
        foreign_keys="Palette.current_depot_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_depots_name_active", "name", "is_active"),
        Index("ix_depots_partner", "partner_id", "is_active"),
        Index("ix_depots_main", "partner_id", "is_main_depot"),
        Index("ix_depots_location", "latitude", "longitude"),
    )
    
    def __repr__(self) -> str:
        """String representation of Depot."""
        return f"<Depot(id={self.id}, name={self.name}, code={self.code})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code]
        return ", ".join(filter(None, parts))
    
    @property
    def has_location(self) -> bool:
        """Check if depot has GPS coordinates."""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def total_capacity(self) -> int:
        """Get total capacity across all palette types."""
        return (self.capacity_b28 or 0) + (self.capacity_b12 or 0) + (self.capacity_b6 or 0)

