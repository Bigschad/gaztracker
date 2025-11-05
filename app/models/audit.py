"""
Audit Log Model

Defines the AuditLog model for tracking all system changes.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AuditLog(Base):
    """
    Audit log model for tracking all system changes and user actions.

    Attributes:
        id: Unique audit log identifier (UUID)
        user_id: User who performed the action
        action: Action performed (CREATE, UPDATE, DELETE, etc.)
        resource_type: Type of resource affected (User, Palette, Expedition, etc.)
        resource_id: ID of the affected resource
        changes: JSON object with before/after values
        ip_address: IP address of the request
        user_agent: User agent string
        endpoint: API endpoint accessed
        http_method: HTTP method used (GET, POST, PUT, DELETE)
        timestamp: When action was performed
        success: Whether the action was successful
        error_message: Error message if action failed
        additional_data: Additional contextual data
    """

    __tablename__ = "audit_logs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique audit log identifier"
    )

    # User Information
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )

    # Action Information
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (CREATE, UPDATE, DELETE, etc.)"
    )

    resource_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of resource affected"
    )

    resource_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID of the affected resource"
    )

    # Changes
    changes = Column(
        JSON,
        nullable=True,
        comment="JSON object with before/after values"
    )

    # Request Information
    ip_address = Column(
        String(45),
        nullable=True,
        index=True,
        comment="IP address of the request"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent string"
    )

    endpoint = Column(
        String(255),
        nullable=True,
        index=True,
        comment="API endpoint accessed"
    )

    http_method = Column(
        String(10),
        nullable=True,
        comment="HTTP method used"
    )

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When action was performed"
    )

    # Result
    success = Column(
        String(10),
        default="true",
        nullable=False,
        index=True,
        comment="Whether the action was successful"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if action failed"
    )

    # Additional Data
    additional_data = Column(
        JSON,
        nullable=True,
        comment="Additional contextual data"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="audit_logs"
    )

    # Indexes
    __table_args__ = (
        Index("ix_audit_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_action_timestamp", "action", "timestamp"),
        Index("ix_audit_success_timestamp", "success", "timestamp"),
    )

    def __repr__(self) -> str:
        """String representation of AuditLog."""
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type})>"

    @classmethod
    def create_log(
        cls,
        user_id: uuid.UUID,
        action: str,
        resource_type: str,
        resource_id: str = None,
        changes: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        http_method: str = None,
        success: bool = True,
        error_message: str = None,
        additional_data: dict = None
    ) -> "AuditLog":
        """
        Create a new audit log entry.

        Args:
            user_id: User who performed the action
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of resource (optional)
            changes: Changes made (optional)
            ip_address: IP address (optional)
            user_agent: User agent (optional)
            endpoint: API endpoint (optional)
            http_method: HTTP method (optional)
            success: Whether action was successful
            error_message: Error message if failed (optional)
            additional_data: Additional data (optional)

        Returns:
            AuditLog: New audit log instance
        """
        return cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            success=str(success).lower(),
            error_message=error_message,
            additional_data=additional_data
        )
