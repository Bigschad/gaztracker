"""
User Model

Defines the User model with role-based access control (RBAC).
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class UserRole(str, enum.Enum):
    """
    User roles for role-based access control.

    - ADMIN: System administrator with full access
    - RESPONSABLE_LOGISTIQUE: Logistics manager at factory
    - OPERATEUR_USINE: Factory operator
    - CHAUFFEUR: Driver/delivery person
    - GROSSISTE: Wholesaler/distributor
    """
    ADMIN = "ADMIN"
    RESPONSABLE_LOGISTIQUE = "RESPONSABLE_LOGISTIQUE"
    OPERATEUR_USINE = "OPERATEUR_USINE"
    CHAUFFEUR = "CHAUFFEUR"
    GROSSISTE = "GROSSISTE"


class User(Base, TimestampMixin):
    """
    User model with authentication and role-based access control.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique)
        password_hash: Hashed password
        first_name: User's first name
        last_name: User's last name
        role: User's role (enum)
        phone_number: User's phone number (optional)
        is_active: Whether the user account is active
        is_verified: Whether the user's email is verified
        company_name: Company name (for GROSSISTE role)
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique user identifier"
    )

    # Authentication
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address"
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password"
    )

    # Personal Information
    first_name = Column(
        String(100),
        nullable=False,
        comment="User first name"
    )

    last_name = Column(
        String(100),
        nullable=False,
        comment="User last name"
    )

    phone_number = Column(
        String(20),
        nullable=True,
        index=True,
        comment="User phone number"
    )

    company_name = Column(
        String(255),
        nullable=True,
        comment="Company name (for GROSSISTE)"
    )

    # Role-Based Access Control
    role = Column(
        SQLEnum(UserRole, name="user_role", create_type=True),
        nullable=False,
        default=UserRole.OPERATEUR_USINE,
        index=True,
        comment="User role for RBAC"
    )

    # Account Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether user account is active"
    )

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user email is verified"
    )

    # Relationships
    created_palettes = relationship(
        "Palette",
        back_populates="created_by",
        foreign_keys="Palette.created_by_id",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    created_expeditions = relationship(
        "Expedition",
        back_populates="created_by",
        foreign_keys="Expedition.created_by_id",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    validated_expeditions = relationship(
        "Expedition",
        back_populates="validated_by",
        foreign_keys="Expedition.validated_by_id",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    palette_movements = relationship(
        "PaletteMovement",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role_active", "role", "is_active"),
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role: UserRole) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: Role to check

        Returns:
            bool: True if user has the role
        """
        return self.role == role

    def has_any_role(self, *roles: UserRole) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            *roles: Roles to check

        Returns:
            bool: True if user has any of the roles
        """
        return self.role in roles

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def is_grossiste(self) -> bool:
        """Check if user is a wholesaler."""
        return self.role == UserRole.GROSSISTE

    def is_chauffeur(self) -> bool:
        """Check if user is a driver."""
        return self.role == UserRole.CHAUFFEUR

    def is_responsable_logistique(self) -> bool:
        """Check if user is a logistics manager."""
        return self.role == UserRole.RESPONSABLE_LOGISTIQUE

    def is_operateur_usine(self) -> bool:
        """Check if user is a factory operator."""
        return self.role == UserRole.OPERATEUR_USINE
