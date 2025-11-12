"""
System Configuration Service

Business logic for managing system-wide configuration.
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

logger = logging.getLogger(__name__)


class SystemConfigService:
    """Service for managing system configuration."""

    @staticmethod
    def get_config(db: Session) -> SystemConfig:
        """
        Get the system configuration.

        Returns the first (and should be only) configuration record.
        If no configuration exists, creates a default one.

        Args:
            db: Database session

        Returns:
            System configuration
        """
        config = db.query(SystemConfig).first()

        if not config:
            # Create default configuration if none exists
            config = SystemConfig(
                factory_name="GazTracker Factory",
                auto_set_factory_location=True
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            logger.info("Created default system configuration")

        return config

    @staticmethod
    def update_config(
        db: Session,
        config_update: SystemConfigUpdate
    ) -> SystemConfig:
        """
        Update the system configuration.

        Args:
            db: Database session
            config_update: Configuration update data

        Returns:
            Updated system configuration
        """
        config = SystemConfigService.get_config(db)

        # Apply updates
        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        db.add(config)
        db.commit()
        db.refresh(config)

        logger.info(f"System configuration updated: {update_data.keys()}")
        return config

    @staticmethod
    def get_factory_location(db: Session) -> Optional[dict]:
        """
        Get factory location details.

        Args:
            db: Database session

        Returns:
            Dictionary with factory location or None if not configured
        """
        config = SystemConfigService.get_config(db)

        if not config.has_factory_location:
            return None

        return {
            "factory_name": config.factory_name,
            "factory_address": config.factory_address,
            "factory_latitude": config.factory_latitude,
            "factory_longitude": config.factory_longitude
        }

    @staticmethod
    def should_auto_set_location(db: Session) -> bool:
        """
        Check if automatic factory location setting is enabled.

        Args:
            db: Database session

        Returns:
            True if auto-set is enabled, False otherwise
        """
        config = SystemConfigService.get_config(db)
        return config.auto_set_factory_location and config.has_factory_location

    @staticmethod
    def initialize_config(
        db: Session,
        config_create: SystemConfigCreate
    ) -> SystemConfig:
        """
        Initialize system configuration (for initial setup).

        This should only be called during initial system setup.
        If configuration already exists, use update_config instead.

        Args:
            db: Database session
            config_create: Configuration creation data

        Returns:
            Created system configuration

        Raises:
            ValidationException: If configuration already exists
        """
        existing = db.query(SystemConfig).first()
        if existing:
            raise ValidationException(
                message="System configuration already exists. Use update endpoint instead.",
                details={"config_id": str(existing.id)}
            )

        config = SystemConfig(**config_create.model_dump())
        db.add(config)
        db.commit()
        db.refresh(config)

        logger.info("System configuration initialized")
        return config
