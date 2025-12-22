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
    contact_name: Optional[str] = Field(None, max_length=255, description="Name of the contact person")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Phone number of the contact person")
    is_active: bool = Field(True, description="Whether the depot is active")
    is_main_depot: bool = Field(False, description="Indicates if this is the main depot for the partner")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


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
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
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
    partner_name: Optional[str] = Field(None, description="Name of the parent partner (grossiste)")
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
    palettes_count: Optional[int] = Field(None, description="Number of palettes currently at depot")
    
    class Config:
        from_attributes = True


# Schema for depot with location
class DepotLocation(BaseModel):
    """Schema for depot location (for maps)."""
    
    id: UUID
    name: str
    address: Optional[str]
    city: Optional[str]
    
    class Config:
        from_attributes = True

