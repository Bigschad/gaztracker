"""
Model Mixins

Common mixins for SQLAlchemy models.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """
    Mixin that adds timestamp columns to models.

    Adds:
        - created_at: Timestamp when record was created
        - updated_at: Timestamp when record was last updated
    """

    @declared_attr
    def created_at(cls):
        """Timestamp when record was created."""
        return Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False,
            index=True,
            comment="Timestamp when record was created"
        )

    @declared_attr
    def updated_at(cls):
        """Timestamp when record was last updated."""
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
            comment="Timestamp when record was last updated"
        )


class SoftDeleteMixin:
    """
    Mixin that adds soft delete functionality to models.

    Adds:
        - is_deleted: Flag indicating if record is deleted
        - deleted_at: Timestamp when record was deleted
    """

    @declared_attr
    def is_deleted(cls):
        """Flag indicating if record is soft deleted."""
        return Column(
            "is_deleted",
            DateTime,
            default=False,
            nullable=False,
            index=True,
            comment="Flag indicating if record is deleted"
        )

    @declared_attr
    def deleted_at(cls):
        """Timestamp when record was soft deleted."""
        return Column(
            DateTime,
            nullable=True,
            comment="Timestamp when record was deleted"
        )

    def soft_delete(self):
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
