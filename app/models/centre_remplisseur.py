"""
Centre Remplisseur Model

Defines the CentreRemplisseur model for filling centers.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Float, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin


class CentreRemplisseur(Base, TimestampMixin):
    """
    Centre Remplisseur model for gas filling centers.
    
    Physical infrastructure for filling and conditioning gas bottles.
    Starting point for shipments.
    
    Attributes:
        id: Unique centre remplisseur identifier (UUID)
        name: Centre name
        code: Unique code
        partner_id: FK to partners (distributeur)
        address: Address
        city: City
        postal_code: Postal code
        country: Country
        phone: Phone number
        email: Email address
        contact_name: Contact person name
        contact_phone: Contact person phone
        is_active: Whether the centre is active
        notes: Additional notes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "centres_remplisseurs"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique centre remplisseur identifier"
    )
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Centre name"
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
        comment="FK to partners (distributeur)"
    )
    
    grand_distributeur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("grand_distributeurs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="FK to grand_distributeurs"
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
    
    country = Column(
        String(100),
        nullable=True,
        default="Côte d'Ivoire",
        comment="Country"
    )
    
    # Contact Information
    phone = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Phone number"
    )
    
    email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email address"
    )
    
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
    
    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether centre is active"
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
        foreign_keys=[partner_id]
    )
    
    grand_distributeur = relationship(
        "GrandDistributeur",
        back_populates="centres_remplisseurs",
        foreign_keys=[grand_distributeur_id]
    )
    
    bons_enlevement = relationship(
        "BonEnlevement",
        back_populates="centre_remplisseur",
        foreign_keys="BonEnlevement.centre_remplisseur_id",
        lazy="dynamic"
    )
    
    bons_reception_retour = relationship(
        "BonReceptionRetour",
        back_populates="centre_remplisseur",
        foreign_keys="BonReceptionRetour.centre_remplisseur_id",
        lazy="dynamic"
    )
    
    palettes = relationship(
        "Palette",
        back_populates="current_centre_remplisseur",
        foreign_keys="Palette.current_centre_remplisseur_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_centres_name_active", "name", "is_active"),
        Index("ix_centres_partner", "partner_id", "is_active"),
        Index("ix_centres_grand_dist", "grand_distributeur_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of CentreRemplisseur."""
        return f"<CentreRemplisseur(id={self.id}, name={self.name}, code={self.code})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

