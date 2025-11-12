"""
Partner Model

Defines the Partner model for storing partner information (grossistes, suppliers, etc.).
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class PartnerType(str, enum.Enum):
    """
    Partner types.
    
    - GROSSISTE: Wholesaler/distributor
    - FOURNISSEUR: Supplier
    - TRANSPORTEUR: Transport company
    - AUTRE: Other
    """
    GROSSISTE = "GROSSISTE"
    FOURNISSEUR = "FOURNISSEUR"
    TRANSPORTEUR = "TRANSPORTEUR"
    AUTRE = "AUTRE"


class Partner(Base, TimestampMixin):
    """
    Partner model for storing partner information.
    
    Attributes:
        id: Unique partner identifier (UUID)
        name: Partner name (company name)
        type: Partner type (enum)
        address: Partner address
        city: City
        postal_code: Postal code
        country: Country
        phone: Phone number
        email: Email address
        is_active: Whether the partner is active
        notes: Additional notes
        created_at: Timestamp when partner was created
        updated_at: Timestamp when partner was last updated
    """
    
    __tablename__ = "partners"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique partner identifier"
    )
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Partner name (company name)"
    )
    
    type = Column(
        SQLEnum(PartnerType, name="partner_type", create_type=False),
        nullable=False,
        default=PartnerType.GROSSISTE,
        index=True,
        comment="Partner type"
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
        default="France",
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
    
    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether partner is active"
    )
    
    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )
    
    # Relationships
    contacts = relationship(
        "Contact",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    expeditions = relationship(
        "Expedition",
        back_populates="grossiste",
        foreign_keys="Expedition.grossiste_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_partners_name_active", "name", "is_active"),
        Index("ix_partners_type_active", "type", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of Partner."""
        return f"<Partner(id={self.id}, name={self.name}, type={self.type})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

