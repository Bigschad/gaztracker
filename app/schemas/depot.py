"""
Depot Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Base schema with common attributes
class DepotBase(BaseModel):
    """Base Depot schema with common attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Name of the depot")
    code: Optional[str] = Field(None, max_length=50, description="Unique code for the depot")
    partner_id: UUID = Field(..., description="Foreign key to the Partner model (grossiste or revendeur)")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of the depot")
    city: Optional[str] = Field(None, max_length=100, description="City where the depot is located")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code of the depot")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    contact_name: Optional[str] = Field(None, max_length=255, description="Name of the contact person")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Phone number of the contact person")
    capacity_b28: Optional[int] = Field(None, ge=0, description="Capacity for B28 palettes")
    capacity_b12: Optional[int] = Field(None, ge=0, description="Capacity for B12 palettes")
    capacity_b6: Optional[int] = Field(None, ge=0, description="Capacity for B6 palettes")
    is_active: bool = Field(True, description="Whether the depot is active")
    is_main_depot: bool = Field(False, description="Indicates if this is the main depot for the partner")
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


# Schema for creating a new Depot
class DepotCreate(DepotBase):
    """Schema for creating a new Depot."""
    pass


# Schema for updating an existing Depot
class DepotUpdate(BaseModel):
    """Schema for updating an existing Depot (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    partner_id: Optional[UUID] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    capacity_b28: Optional[int] = Field(None, ge=0)
    capacity_b12: Optional[int] = Field(None, ge=0)
    capacity_b6: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_main_depot: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


# Schema for reading a Depot (includes ID and timestamps)
class DepotRead(DepotBase):
    """Schema for reading a Depot."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing Depots (minimal info)
class DepotList(BaseModel):
    """Schema for listing Depots (minimal info for dropdowns, etc.)."""
    
    id: UUID
    name: str
    code: Optional[str]
    partner_id: UUID
    city: Optional[str]
    is_active: bool
    is_main_depot: bool
    
    class Config:
        from_attributes = True


# Schema with related data
class DepotDetail(DepotRead):
    """Schema for detailed Depot with related data."""
    
    partner_name: Optional[str] = Field(None, description="Name of the parent partner")
    partner_type: Optional[str] = Field(None, description="Type of the parent partner")
    total_capacity: Optional[int] = Field(None, description="Total capacity across all palette types")
    palettes_count: Optional[int] = Field(None, description="Number of palettes currently at depot")
    
    class Config:
        from_attributes = True


# Schema for depot with GPS location
class DepotLocation(BaseModel):
    """Schema for depot location (for maps)."""
    
    id: UUID
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    city: Optional[str]
    
    class Config:
        from_attributes = True

