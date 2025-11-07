"""
Expedition Schemas

Pydantic schemas for Expedition model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.expedition import ExpeditionStatus


# =============================================================================
# Base Schemas
# =============================================================================

class ExpeditionBase(BaseModel):
    """Base expedition schema with common fields."""

    destination_address: str = Field(..., max_length=500, description="Delivery address")
    destination_contact: Optional[str] = Field(None, max_length=255, description="Contact person")
    destination_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    transporter: Optional[str] = Field(None, max_length=255, description="Transport company/driver")
    vehicle_info: Optional[str] = Field(None, max_length=255, description="Vehicle information")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


# =============================================================================
# Request Schemas
# =============================================================================

class ExpeditionCreate(ExpeditionBase):
    """Schema for creating a new expedition."""

    eta: Optional[datetime] = Field(None, description="Estimated time of arrival")
    palette_ids: list[UUID] = Field(default_factory=list, description="List of palette IDs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "destination_address": "123 Rue de Commerce, 75015 Paris",
                "destination_contact": "Jean Dupont",
                "destination_phone": "+33612345678",
                "transporter": "Transport Express",
                "vehicle_info": "Camion AB-123-CD",
                "eta": "2024-01-20T14:00:00Z",
                "notes": "Livraison urgente",
                "palette_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }
    )


class ExpeditionUpdate(BaseModel):
    """Schema for updating an existing expedition."""

    status: Optional[ExpeditionStatus] = Field(None, description="Expedition status")
    destination_address: Optional[str] = Field(None, max_length=500, description="Delivery address")
    destination_contact: Optional[str] = Field(None, max_length=255, description="Contact person")
    destination_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    transporter: Optional[str] = Field(None, max_length=255, description="Transport company/driver")
    vehicle_info: Optional[str] = Field(None, max_length=255, description="Vehicle information")
    eta: Optional[datetime] = Field(None, description="Estimated time of arrival")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    problem_description: Optional[str] = Field(None, max_length=1000, description="Problem description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "EN_TRANSIT",
                "eta": "2024-01-20T15:00:00Z",
                "notes": "Retard prévu"
            }
        }
    )


class ExpeditionDepartRequest(BaseModel):
    """Schema for marking expedition as departed."""

    date_departure: Optional[datetime] = Field(None, description="Departure date (defaults to now)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date_departure": "2024-01-15T08:00:00Z"
            }
        }
    )


class ExpeditionValidateRequest(BaseModel):
    """Schema for validating delivery with OTP."""

    otp_code: str = Field(..., min_length=6, max_length=6, description="OTP code")
    notes: Optional[str] = Field(None, max_length=1000, description="Delivery notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "otp_code": "123456",
                "notes": "Livraison conforme"
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class ExpeditionResponse(ExpeditionBase):
    """Schema for expedition response."""

    id: UUID = Field(..., description="Expedition ID")
    reference_number: str = Field(..., description="Unique reference number")
    status: ExpeditionStatus = Field(..., description="Current status")
    date_creation: datetime = Field(..., description="Creation date")
    date_departure: Optional[datetime] = Field(None, description="Departure date")
    eta: Optional[datetime] = Field(None, description="Estimated time of arrival")
    date_arrival: Optional[datetime] = Field(None, description="Actual arrival date")
    date_delivery: Optional[datetime] = Field(None, description="Delivery date")
    palette_count: int = Field(..., description="Number of palettes")
    otp_code: Optional[str] = Field(None, description="OTP code for validation")
    otp_expiry: Optional[datetime] = Field(None, description="OTP expiration")
    problem_description: Optional[str] = Field(None, description="Problem description")
    created_by_id: Optional[UUID] = Field(None, description="Creator user ID")
    validated_by_id: Optional[UUID] = Field(None, description="Validator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "reference_number": "EXP-20240115-12345",
                "status": "EN_TRANSIT",
                "date_creation": "2024-01-15T08:00:00Z",
                "date_departure": "2024-01-15T09:00:00Z",
                "eta": "2024-01-15T14:00:00Z",
                "date_arrival": None,
                "date_delivery": None,
                "destination_address": "123 Rue de Commerce, Paris",
                "destination_contact": "Jean Dupont",
                "destination_phone": "+33612345678",
                "transporter": "Transport Express",
                "vehicle_info": "AB-123-CD",
                "palette_count": 5,
                "otp_code": "123456",
                "otp_expiry": "2024-01-15T14:15:00Z",
                "notes": None,
                "problem_description": None,
                "created_by_id": "123e4567-e89b-12d3-a456-426614174001",
                "validated_by_id": None,
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-15T09:00:00Z"
            }
        }
    )


class ExpeditionListResponse(BaseModel):
    """Schema for paginated expedition list response."""

    items: list[ExpeditionResponse] = Field(..., description="List of expeditions")
    total: int = Field(..., description="Total number of expeditions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 20,
                "expeditions": []
            }
        }
    )


class ExpeditionStatistics(BaseModel):
    """Schema for expedition statistics."""

    total_expeditions: int = Field(..., description="Total number of expeditions")
    by_status: dict[str, int] = Field(..., description="Count by status")
    in_transit: int = Field(..., description="Expeditions in transit")
    delivered: int = Field(..., description="Delivered expeditions")
    delayed: int = Field(..., description="Delayed expeditions")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_expeditions": 150,
                "by_status": {
                    "CREEE": 20,
                    "EN_TRANSIT": 50,
                    "LIVREE": 70,
                    "PROBLEME": 10
                },
                "in_transit": 50,
                "delivered": 70,
                "delayed": 5
            }
        }
    )
