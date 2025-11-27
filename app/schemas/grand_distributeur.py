"""
Grand Distributeur Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Base schema with common attributes
class GrandDistributeurBase(BaseModel):
    """Base GrandDistributeur schema with common attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Name of the grand distributor")
    code: str = Field(..., min_length=1, max_length=50, description="Unique code for the grand distributor")
    groupe_id: UUID = Field(..., description="Foreign key to the Groupe model")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of the grand distributor")
    city: Optional[str] = Field(None, max_length=100, description="City where the grand distributor is located")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the grand distributor")
    email: Optional[EmailStr] = Field(None, description="Email address of the grand distributor")
    is_active: bool = Field(True, description="Whether the grand distributor is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes about the grand distributor")


# Schema for creating a new GrandDistributeur
class GrandDistributeurCreate(GrandDistributeurBase):
    """Schema for creating a new GrandDistributeur."""
    pass


# Schema for updating an existing GrandDistributeur
class GrandDistributeurUpdate(BaseModel):
    """Schema for updating an existing GrandDistributeur (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    groupe_id: Optional[UUID] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


# Schema for reading a GrandDistributeur (includes ID and timestamps)
class GrandDistributeurRead(GrandDistributeurBase):
    """Schema for reading a GrandDistributeur."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing GrandDistributeurs (minimal info)
class GrandDistributeurList(BaseModel):
    """Schema for listing GrandDistributeurs (minimal info for dropdowns, etc.)."""
    
    id: UUID
    name: str
    code: str
    groupe_id: UUID
    is_active: bool
    
    class Config:
        from_attributes = True


# Schema with related data
class GrandDistributeurDetail(GrandDistributeurRead):
    """Schema for detailed GrandDistributeur with related data."""
    
    groupe_name: Optional[str] = Field(None, description="Name of the parent groupe")
    centres_remplisseurs_count: Optional[int] = Field(None, description="Number of centres remplisseurs")
    
    class Config:
        from_attributes = True

