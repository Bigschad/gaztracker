"""
Centre Remplisseur Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# Base schema with common attributes
class CentreRemplisseurBase(BaseModel):
    """Base CentreRemplisseur schema with common attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Name of the filling center")
    code: str = Field(..., min_length=1, max_length=50, description="Unique code for the filling center")
    grand_distributeur_id: UUID = Field(..., description="Foreign key to the GrandDistributeur model")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of the filling center")
    city: Optional[str] = Field(None, max_length=100, description="City where the filling center is located")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code of the filling center")
    country: Optional[str] = Field("Côte d'Ivoire", max_length=100, description="Country of the filling center")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the filling center")
    email: Optional[EmailStr] = Field(None, description="Email address of the filling center")
    contact_name: Optional[str] = Field(None, max_length=255, description="Name of the contact person")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Phone number of the contact person")
    is_active: bool = Field(True, description="Whether the filling center is active")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator('latitude', 'longitude')
    @classmethod
    def validate_coordinates(cls, v, info):
        """Validate GPS coordinates."""
        if v is not None:
            if info.field_name == 'latitude' and not (-90 <= v <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if info.field_name == 'longitude' and not (-180 <= v <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v


# Schema for creating a new CentreRemplisseur
class CentreRemplisseurCreate(CentreRemplisseurBase):
    """Schema for creating a new CentreRemplisseur."""
    pass


# Schema for updating an existing CentreRemplisseur
class CentreRemplisseurUpdate(BaseModel):
    """Schema for updating an existing CentreRemplisseur (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    grand_distributeur_id: Optional[UUID] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=1000)


# Schema for reading a CentreRemplisseur (includes ID and timestamps)
class CentreRemplisseurRead(CentreRemplisseurBase):
    """Schema for reading a CentreRemplisseur."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing CentreRemplisseurs (minimal info)
class CentreRemplisseurList(BaseModel):
    """Schema for listing CentreRemplisseurs (minimal info for dropdowns, etc.)."""
    
    id: UUID
    name: str
    code: str
    grand_distributeur_id: UUID
    city: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


# Schema with related data
class CentreRemplisseurDetail(CentreRemplisseurRead):
    """Schema for detailed CentreRemplisseur with related data."""
    
    grand_distributeur_name: Optional[str] = Field(None, description="Name of the parent grand distributeur")
    groupe_name: Optional[str] = Field(None, description="Name of the parent groupe")
    bons_enlevement_count: Optional[int] = Field(None, description="Number of bons d'enlèvement")
    bons_retour_count: Optional[int] = Field(None, description="Number of bons de réception retour")
    
    class Config:
        from_attributes = True

