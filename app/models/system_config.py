"""
System Configuration Model

Stores system-wide configuration parameters including factory location.
"""

from sqlalchemy import Column, String, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.database import Base
from app.models.mixins import TimestampMixin


class SystemConfig(Base, TimestampMixin):
    """
    System configuration model for storing application-wide settings.

    This is a singleton-like table that should contain only one row.
    All system configuration is stored here including:
    - Factory location (GPS coordinates and address)
    - Default values for palette creation
    - Other system-wide settings
    """

    __tablename__ = "system_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Factory Location Settings
    factory_name = Column(
        String(200),
        nullable=False,
        default="GazTracker Factory",
        comment="Name of the factory/plant"
    )

    factory_address = Column(
        String(500),
        nullable=True,
        comment="Full address of the factory (Google Maps format)"
    )

    factory_latitude = Column(
        Float,
        nullable=True,
        comment="Factory GPS latitude"
    )

    factory_longitude = Column(
        Float,
        nullable=True,
        comment="Factory GPS longitude"
    )

    # Contact Information
    factory_phone = Column(
        String(50),
        nullable=True,
        comment="Factory contact phone number"
    )

    factory_email = Column(
        String(200),
        nullable=True,
        comment="Factory contact email"
    )

    # System Settings
    auto_set_factory_location = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Automatically set factory location when creating palettes"
    )

    # Additional metadata
    company_name = Column(
        String(200),
        nullable=True,
        comment="Company name"
    )

    def __repr__(self) -> str:
        """String representation of SystemConfig."""
        return f"<SystemConfig(factory={self.factory_name})>"

    @property
    def has_factory_location(self) -> bool:
        """Check if factory location is configured."""
        return (
            self.factory_latitude is not None
            and self.factory_longitude is not None
            and self.factory_address is not None
        )
