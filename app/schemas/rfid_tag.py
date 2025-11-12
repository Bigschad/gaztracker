"""
RFID Tag Schemas

Pydantic schemas for RFID Tag model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.rfid_tag import RFIDTagStatus


# =============================================================================
# Base Schemas
# =============================================================================

class RFIDTagBase(BaseModel):
    """Base RFID tag schema with common fields."""

    tag_number: str = Field(..., min_length=1, max_length=50, description="Unique RFID tag number")
    label: Optional[str] = Field(None, max_length=255, description="Label/name for the RFID tag")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


# =============================================================================
# Request Schemas
# =============================================================================

class RFIDTagCreate(RFIDTagBase):
    """Schema for creating a new RFID tag."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag_number": "RFID-2024-001",
                "notes": "Tag created from mobile - Site A"
            }
        }
    )


class RFIDTagUpdate(BaseModel):
    """Schema for updating an existing RFID tag."""

    label: Optional[str] = Field(None, max_length=255, description="Label/name for the RFID tag")
    status: Optional[RFIDTagStatus] = Field(None, description="Tag status")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    is_active: Optional[bool] = Field(None, description="Active status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "LOST",
                "notes": "Tag lost during transport"
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class RFIDTagResponse(BaseModel):
    """Schema for RFID tag response."""

    id: UUID = Field(..., description="Tag ID")
    tag_number: str = Field(..., description="RFID tag number")
    label: Optional[str] = Field(None, description="Label/name for the RFID tag")
    status: RFIDTagStatus = Field(..., description="Tag status")
    created_by_id: UUID = Field(..., description="Creator user ID")
    is_active: bool = Field(..., description="Active status")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tag_number": "RFID-2024-001",
                "status": "NOT_ASSIGNED",
                "created_by_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_active": True,
                "notes": "Tag created from mobile",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "assigned_at": None
            }
        }
    )


class RFIDTagDetailResponse(RFIDTagResponse):
    """Schema for detailed RFID tag response with palette information."""

    palette_id: Optional[UUID] = Field(None, description="Associated palette ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tag_number": "RFID-2024-001",
                "status": "ASSIGNED",
                "created_by_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_active": True,
                "notes": "Tag assigned to palette",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z",
                "assigned_at": "2024-01-15T10:35:00Z",
                "palette_id": "660e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


class RFIDTagListResponse(BaseModel):
    """Schema for paginated RFID tag list response."""

    items: list[RFIDTagResponse] = Field(..., description="List of RFID tags")
    total: int = Field(..., description="Total number of tags")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    filters: dict = Field(default_factory=dict, description="Applied filters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 20,
                "tags": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "tag_number": "RFID-2024-001",
                        "status": "NOT_ASSIGNED",
                        "created_by_id": "123e4567-e89b-12d3-a456-426614174000",
                        "is_active": True,
                        "notes": None,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                        "assigned_at": None
                    }
                ],
                "filters": {
                    "status": "NOT_ASSIGNED",
                    "skip": 0,
                    "limit": 20
                }
            }
        }
    )


# =============================================================================
# Statistics Schemas
# =============================================================================

class RFIDTagStatistics(BaseModel):
    """Schema for RFID tag statistics."""

    total_tags: int = Field(..., description="Total number of tags")
    by_status: dict[str, int] = Field(..., description="Count by status")
    not_assigned: int = Field(..., description="Tags not assigned")
    assigned: int = Field(..., description="Tags assigned")
    lost: int = Field(..., description="Tags lost")
    damaged: int = Field(..., description="Tags damaged")
    active: int = Field(..., description="Active tags")
    inactive: int = Field(..., description="Inactive tags")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_tags": 150,
                "by_status": {
                    "NOT_ASSIGNED": 50,
                    "ASSIGNED": 80,
                    "LOST": 15,
                    "DAMAGED": 5
                },
                "not_assigned": 50,
                "assigned": 80,
                "lost": 15,
                "damaged": 5,
                "active": 140,
                "inactive": 10
            }
        }
    )
