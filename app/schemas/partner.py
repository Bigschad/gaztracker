"""
Partner Schemas

Pydantic schemas for Partner model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID

from app.models.partner import PartnerType
from app.schemas.groupe import GroupeRead


# =============================================================================
# Base Schemas
# =============================================================================

class PartnerBase(BaseModel):
    """Base partner schema with common fields."""
    
    name: str = Field(..., max_length=255, description="Partner name (company name)")
    type: PartnerType = Field(..., description="Partner type")
    groupe_id: Optional[UUID] = Field(None, description="FK to groupe (for DISTRIBUTEUR only)")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    country: Optional[str] = Field(default="France", max_length=100, description="Country")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Email address")
    is_active: bool = Field(default=True, description="Whether partner is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


# =============================================================================
# Request Schemas
# =============================================================================

class PartnerCreate(PartnerBase):
    """Schema for creating a new partner."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Grossiste Paris Nord",
                "type": "GROSSISTE",
                "address": "123 Rue de Commerce",
                "city": "Paris",
                "postal_code": "75015",
                "country": "France",
                "phone": "+33123456789",
                "email": "contact@grossiste-paris-nord.fr",
                "is_active": True,
                "notes": "Principal grossiste pour la région parisienne"
            }
        }
    )


class PartnerUpdate(BaseModel):
    """Schema for updating an existing partner."""
    
    name: Optional[str] = Field(None, max_length=255, description="Partner name")
    type: Optional[PartnerType] = Field(None, description="Partner type")
    groupe_id: Optional[UUID] = Field(None, description="FK to groupe (for DISTRIBUTEUR only)")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Email address")
    is_active: Optional[bool] = Field(None, description="Whether partner is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


# =============================================================================
# Response Schemas
# =============================================================================

class PartnerResponse(PartnerBase):
    """Schema for partner response."""
    
    id: UUID = Field(..., description="Partner ID")
    groupe: Optional[GroupeRead] = Field(None, description="Groupe details (for DISTRIBUTEUR only)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Grossiste Paris Nord",
                "type": "GROSSISTE",
                "address": "123 Rue de Commerce",
                "city": "Paris",
                "postal_code": "75015",
                "country": "France",
                "phone": "+33123456789",
                "email": "contact@grossiste-paris-nord.fr",
                "is_active": True,
                "notes": "Principal grossiste pour la région parisienne",
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-15T08:00:00Z"
            }
        }
    )


class PartnerListResponse(BaseModel):
    """Schema for paginated partner list response."""
    
    items: list[PartnerResponse] = Field(..., description="List of partners")
    total: int = Field(..., description="Total number of partners")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

