"""
Partner Model

Defines the Partner model for storing partner information (grossistes, suppliers, etc.).
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index, ForeignKey
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
    - DISTRIBUTEUR: Distributor
    - REVENDEUR: Reseller (client of grossiste)
    - TRANSPORTEUR: Transport company
    - AUTRE: Other
    """
    GROSSISTE = "GROSSISTE"
    DISTRIBUTEUR = "DISTRIBUTEUR"
    REVENDEUR = "REVENDEUR"
    TRANSPORTEUR = "TRANSPORTEUR"
    AUTRE = "AUTRE"


class Partner(Base, TimestampMixin):
    """
    Partner model for storing partner information.
    
    Attributes:
        id: Unique partner identifier (UUID)
        name: Partner name (company name)
        type: Partner type (enum)
        code: Unique code (client ID)
        parent_grossiste_id: FK to parent grossiste (for REVENDEUR only)
        address: Partner address
        city: City
        postal_code: Postal code
        country: Country
        phone: Phone number
        email: Email address
        contact_name: Contact person name
        contact_phone: Contact person phone
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
    
    code = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Unique code (client ID)"
    )
    
    # For REVENDEUR: link to parent grossiste
    parent_grossiste_id = Column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to parent grossiste (for REVENDEUR only)"
    )
    
    # For DISTRIBUTEUR: link to groupe
    groupe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groupes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to groupe (for DISTRIBUTEUR only)"
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
    
    # New relationships for corrected structure
    parent_grossiste = relationship(
        "Partner",
        remote_side=[id],
        back_populates="revendeurs",
        foreign_keys=[parent_grossiste_id]
    )
    
    revendeurs = relationship(
        "Partner",
        back_populates="parent_grossiste",
        foreign_keys=[parent_grossiste_id]
    )
    
    depots = relationship(
        "Depot",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    livraisons_details = relationship(
        "LivraisonDetail",
        back_populates="revendeur",
        foreign_keys="LivraisonDetail.revendeur_id",
        lazy="dynamic"
    )
    
    bons_enlevement = relationship(
        "BonEnlevement",
        back_populates="grossiste",
        foreign_keys="BonEnlevement.grossiste_id",
        lazy="dynamic"
    )
    
    livraisons_details = relationship(
        "LivraisonDetail",
        back_populates="revendeur",
        foreign_keys="LivraisonDetail.revendeur_id",
        lazy="dynamic"
    )
    
    bons_reception_retour = relationship(
        "BonReceptionRetour",
        back_populates="grossiste",
        foreign_keys="BonReceptionRetour.grossiste_id",
        lazy="dynamic"
    )
    
    palettes = relationship(
        "Palette",
        back_populates="current_partner",
        foreign_keys="Palette.current_partner_id",
        lazy="dynamic"
    )
    
    groupe = relationship(
        "Groupe",
        foreign_keys=[groupe_id],
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_partners_name_active", "name", "is_active"),
        Index("ix_partners_type_active", "type", "is_active"),
        Index("ix_partners_parent", "parent_grossiste_id"),
    )
    
    def __repr__(self) -> str:
        """String representation of Partner."""
        return f"<Partner(id={self.id}, name={self.name}, type={self.type})>"
    
    @property
    def full_address(self) -> str:
        """Get full address as a string."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

