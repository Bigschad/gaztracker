"""
Contact Model

Defines the Contact model for storing contact information for partners.
Contacts are people who are not users of the system (e.g., contact at grossiste, driver, etc.).
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.mixins import TimestampMixin


class Contact(Base, TimestampMixin):
    """
    Contact model for storing contact information.
    
    Attributes:
        id: Unique contact identifier (UUID)
        partner_id: Partner this contact belongs to (FK)
        first_name: Contact first name
        last_name: Contact last name
        position: Job position/title
        phone: Phone number
        email: Email address
        is_primary: Whether this is the primary contact for the partner
        notes: Additional notes
        created_at: Timestamp when contact was created
        updated_at: Timestamp when contact was last updated
    """
    
    __tablename__ = "contacts"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique contact identifier"
    )
    
    # Foreign Keys
    partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Partner this contact belongs to"
    )
    
    # Personal Information
    first_name = Column(
        String(100),
        nullable=False,
        comment="Contact first name"
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        comment="Contact last name"
    )
    
    position = Column(
        String(100),
        nullable=True,
        comment="Job position/title"
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
    is_primary = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this is the primary contact"
    )
    
    # Additional Information
    notes = Column(
        String(500),
        nullable=True,
        comment="Additional notes"
    )
    
    # Relationships
    partner = relationship(
        "Partner",
        back_populates="contacts"
    )
    
    expeditions = relationship(
        "Expedition",
        back_populates="contact",
        foreign_keys="Expedition.contact_id",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_contacts_partner_id", "partner_id"),
        Index("ix_contacts_name", "first_name", "last_name"),
    )
    
    def __repr__(self) -> str:
        """String representation of Contact."""
        return f"<Contact(id={self.id}, name={self.full_name}, partner_id={self.partner_id})>"
    
    @property
    def full_name(self) -> str:
        """Get contact's full name."""
        return f"{self.first_name} {self.last_name}"

