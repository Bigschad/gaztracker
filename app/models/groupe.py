"""
Groupe Model

Defines the Groupe model for gas supplier groups.
"""

from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin


class Groupe(Base, TimestampMixin):
    """
    Groupe model for gas supplier groups.
    
    Represents major gas supplier entities (Pétroci Holding, SODIGAZ, etc.)
    
    Attributes:
        id: Unique groupe identifier (UUID)
        name: Groupe name (e.g., "Pétroci Holding")
        code: Unique code (e.g., "PETROCI")
        address: Address
        city: City
        postal_code: Postal code
        country: Country
        phone: Phone number
        email: Email address
        is_active: Whether the groupe is active
        notes: Additional notes
        created_at: Timestamp when groupe was created
        updated_at: Timestamp when groupe was last updated
    """
    
    __tablename__ = "groupes"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique groupe identifier"
    )
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Groupe name"
    )
    
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique code"
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
    
    logo_url = Column(
        String(500),
        nullable=True,
        comment="URL or path to the group logo"
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
    
    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether groupe is active"
    )
    
    # Additional Information
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )
    
    # Relationships
    grand_distributeurs = relationship(
        "GrandDistributeur",
        back_populates="groupe",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_groupes_name_active", "name", "is_active"),
        Index("ix_groupes_code_active", "code", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of Groupe."""
        return f"<Groupe(id={self.id}, name={self.name}, code={self.code})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

