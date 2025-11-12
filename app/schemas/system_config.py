"""
System Configuration Schemas

Pydantic schemas for SystemConfig model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID


# =============================================================================
# Base Schemas
# =============================================================================

class SystemConfigBase(BaseModel):
    """Base system configuration schema with common fields."""

    factory_name: str = Field(..., min_length=1, max_length=200, description="Factory name")
    factory_address: Optional[str] = Field(None, max_length=500, description="Factory address (Google Maps format)")
    factory_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Factory GPS latitude")
    factory_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Factory GPS longitude")
    factory_phone: Optional[str] = Field(None, max_length=50, description="Factory phone number")
    factory_email: Optional[EmailStr] = Field(None, description="Factory email")
    auto_set_factory_location: bool = Field(True, description="Auto-set factory location on palette creation")
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")


# =============================================================================
# Request Schemas
# =============================================================================

class SystemConfigCreate(SystemConfigBase):
    """Schema for creating system configuration (initial setup)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "factory_name": "GazTracker Factory - Site Principal",
                "factory_address": "123 Rue de l'Industrie, 75001 Paris, France",
                "factory_latitude": 48.8566,
                "factory_longitude": 2.3522,
                "factory_phone": "+33 1 23 45 67 89",
                "factory_email": "factory@gaztracker.com",
                "auto_set_factory_location": True,
                "company_name": "GazTracker SARL"
            }
        }
    )


class SystemConfigUpdate(BaseModel):
    """Schema for updating system configuration."""

    factory_name: Optional[str] = Field(None, min_length=1, max_length=200)
    factory_address: Optional[str] = Field(None, max_length=500)
    factory_latitude: Optional[float] = Field(None, ge=-90, le=90)
    factory_longitude: Optional[float] = Field(None, ge=-180, le=180)
    factory_phone: Optional[str] = Field(None, max_length=50)
    factory_email: Optional[EmailStr] = None
    auto_set_factory_location: Optional[bool] = None
    company_name: Optional[str] = Field(None, max_length=200)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "factory_address": "456 Avenue Nouvelle, 75002 Paris, France",
                "factory_latitude": 48.8606,
                "factory_longitude": 2.3376
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class SystemConfigResponse(SystemConfigBase):
    """Schema for system configuration response."""

    id: UUID = Field(..., description="Configuration ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "factory_name": "GazTracker Factory - Site Principal",
                "factory_address": "123 Rue de l'Industrie, 75001 Paris, France",
                "factory_latitude": 48.8566,
                "factory_longitude": 2.3522,
                "factory_phone": "+33 1 23 45 67 89",
                "factory_email": "factory@gaztracker.com",
                "auto_set_factory_location": True,
                "company_name": "GazTracker SARL",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class FactoryLocationResponse(BaseModel):
    """Simplified schema for factory location only."""

    factory_name: str
    factory_address: Optional[str]
    factory_latitude: Optional[float]
    factory_longitude: Optional[float]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "factory_name": "GazTracker Factory - Site Principal",
                "factory_address": "123 Rue de l'Industrie, 75001 Paris, France",
                "factory_latitude": 48.8566,
                "factory_longitude": 2.3522
            }
        }
    )
