"""
Grand Distributeur Model

Defines the GrandDistributeur model for major distributors.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin


class GrandDistributeur(Base, TimestampMixin):
    """
    Grand Distributeur model for major distributors.
    
    Operates on behalf of a Groupe and manages multiple filling centers.
    
    Attributes:
        id: Unique grand distributeur identifier (UUID)
        name: Grand distributeur name (e.g., "CEV3 (PETROCI)")
        code: Unique code
        groupe_id: FK to groupes
        address: Address
        city: City
        postal_code: Postal code
        country: Country
        phone: Phone number
        email: Email address
        contact_name: Contact person name
        contact_phone: Contact person phone
        is_active: Whether the grand distributeur is active
        notes: Additional notes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    
    __tablename__ = "grand_distributeurs"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique grand distributeur identifier"
    )
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Grand distributeur name"
    )
    
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique code"
    )
    
    # Foreign Keys
    groupe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groupes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to groupes"
    )
    
    # Address Information
    address = Column(
        String(500),
        nullable=True,
        comment="Street address"
    )
    
    city = Column(
        String(100),
        nullable=True,
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
        comment="Whether grand distributeur is active"
    )
    
    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )
    
    # Relationships
    groupe = relationship(
        "Groupe",
        back_populates="grand_distributeurs"
    )
    
    centres_remplisseurs = relationship(
        "CentreRemplisseur",
        back_populates="grand_distributeur",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_grand_dist_name_active", "name", "is_active"),
        Index("ix_grand_dist_groupe", "groupe_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of GrandDistributeur."""
        return f"<GrandDistributeur(id={self.id}, name={self.name}, code={self.code})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

