"""
Groupe Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Base schema with common attributes
class GroupeBase(BaseModel):
    """Base Groupe schema with common attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Name of the group")
    code: str = Field(..., min_length=1, max_length=50, description="Unique code for the group")
    address: Optional[str] = Field(None, max_length=500, description="Physical address of the group")
    city: Optional[str] = Field(None, max_length=100, description="City where the group is located")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the group")
    email: Optional[EmailStr] = Field(None, description="Email address of the group")
    logo_url: Optional[str] = Field(None, max_length=500, description="URL or path to the group logo")
    is_active: bool = Field(True, description="Whether the group is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes about the group")


# Schema for creating a new Groupe
class GroupeCreate(GroupeBase):
    """Schema for creating a new Groupe."""
    pass


# Schema for updating an existing Groupe
class GroupeUpdate(BaseModel):
    """Schema for updating an existing Groupe (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


# Schema for reading a Groupe (includes ID and timestamps)
class GroupeRead(GroupeBase):
    """Schema for reading a Groupe."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing Groupes (minimal info)
class GroupeList(BaseModel):
    """Schema for listing Groupes (minimal info for dropdowns, etc.)."""
    
    id: UUID
    name: str
    code: str
    logo_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Schema with related data
class GroupeDetail(GroupeRead):
    """Schema for detailed Groupe with related grand_distributeurs count."""
    
    grand_distributeurs_count: Optional[int] = Field(None, description="Number of grand distributeurs")
    
    class Config:
        from_attributes = True

