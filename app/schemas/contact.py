"""
Contact Schemas

Pydantic schemas for Contact model validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID


# =============================================================================
# Base Schemas
# =============================================================================

class ContactBase(BaseModel):
    """Base contact schema with common fields."""
    
    partner_id: UUID = Field(..., description="Partner this contact belongs to")
    first_name: str = Field(..., max_length=100, description="Contact first name")
    last_name: str = Field(..., max_length=100, description="Contact last name")
    position: Optional[str] = Field(None, max_length=100, description="Job position/title")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Email address")
    is_primary: bool = Field(default=False, description="Whether this is the primary contact")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


# =============================================================================
# Request Schemas
# =============================================================================

class ContactCreate(ContactBase):
    """Schema for creating a new contact."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "partner_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "Jean",
                "last_name": "Dupont",
                "position": "Responsable logistique",
                "phone": "+33612345678",
                "email": "jean.dupont@grossiste.fr",
                "is_primary": True,
                "notes": "Contact principal pour les livraisons"
            }
        }
    )


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact."""
    
    partner_id: Optional[UUID] = Field(None, description="Partner this contact belongs to")
    first_name: Optional[str] = Field(None, max_length=100, description="Contact first name")
    last_name: Optional[str] = Field(None, max_length=100, description="Contact last name")
    position: Optional[str] = Field(None, max_length=100, description="Job position/title")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Email address")
    is_primary: Optional[bool] = Field(None, description="Whether this is the primary contact")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


# =============================================================================
# Response Schemas
# =============================================================================

class ContactResponse(ContactBase):
    """Schema for contact response."""
    
    id: UUID = Field(..., description="Contact ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "partner_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "Jean",
                "last_name": "Dupont",
                "position": "Responsable logistique",
                "phone": "+33612345678",
                "email": "jean.dupont@grossiste.fr",
                "is_primary": True,
                "notes": "Contact principal pour les livraisons",
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-15T08:00:00Z"
            }
        }
    )


class ContactListResponse(BaseModel):
    """Schema for paginated contact list response."""
    
    items: list[ContactResponse] = Field(..., description="List of contacts")
    total: int = Field(..., description="Total number of contacts")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

