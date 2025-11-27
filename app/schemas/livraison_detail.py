"""
Livraison Detail Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.livraison_detail import LivraisonStatus


# Base schema with common attributes
class LivraisonDetailBase(BaseModel):
    """Base LivraisonDetail schema with common attributes."""
    
    bon_enlevement_id: UUID = Field(..., description="Foreign key to bons_enlevement")
    ordre_livraison: int = Field(..., ge=1, description="Order in tour (1, 2, 3...)")
    depot_id: UUID = Field(..., description="Foreign key to depots")
    revendeur_id: Optional[UUID] = Field(None, description="Foreign key to partners (if revendeur)")
    observations: Optional[str] = Field(None, max_length=1000, description="Observations")


# Schema for creating a new LivraisonDetail
class LivraisonDetailCreate(LivraisonDetailBase):
    """Schema for creating a new LivraisonDetail."""
    pass


# Schema for updating an existing LivraisonDetail
class LivraisonDetailUpdate(BaseModel):
    """Schema for updating an existing LivraisonDetail (all fields optional)."""
    
    ordre_livraison: Optional[int] = Field(None, ge=1)
    depot_id: Optional[UUID] = None
    revendeur_id: Optional[UUID] = None
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for reading a LivraisonDetail (includes ID and timestamps)
class LivraisonDetailRead(LivraisonDetailBase):
    """Schema for reading a LivraisonDetail."""
    
    id: UUID
    status: LivraisonStatus
    date_arrivee: Optional[datetime]
    date_depart: Optional[datetime]
    recepteur_nom: Optional[str]
    recepteur_signature: Optional[str]
    problemes: Optional[str]
    latitude_arrivee: Optional[float]
    longitude_arrivee: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing LivraisonDetails (minimal info)
class LivraisonDetailList(BaseModel):
    """Schema for listing LivraisonDetails (minimal info)."""
    
    id: UUID
    bon_enlevement_id: UUID
    ordre_livraison: int
    depot_id: UUID
    status: LivraisonStatus
    date_arrivee: Optional[datetime]
    
    class Config:
        from_attributes = True


# Schema with related data
class LivraisonDetailDetail(LivraisonDetailRead):
    """Schema for detailed LivraisonDetail with related data."""
    
    depot_name: Optional[str] = Field(None, description="Name of the depot")
    revendeur_name: Optional[str] = Field(None, description="Name of the revendeur")
    palettes_count: Optional[int] = Field(None, description="Number of palettes delivered")
    collectes_count: Optional[int] = Field(None, description="Number of empty collections")
    
    class Config:
        from_attributes = True


# Schema for status updates
class LivraisonDetailStatusUpdate(BaseModel):
    """Schema for updating LivraisonDetail status."""
    
    status: LivraisonStatus
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for arrival
class LivraisonDetailArrivee(BaseModel):
    """Schema for arrival at delivery point."""
    
    date_arrivee: Optional[datetime] = None
    latitude_arrivee: Optional[float] = Field(None, ge=-90, le=90)
    longitude_arrivee: Optional[float] = Field(None, ge=-180, le=180)
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for delivery completion
class LivraisonDetailCompletion(BaseModel):
    """Schema for completing a delivery."""
    
    recepteur_nom: str = Field(..., min_length=1, max_length=255, description="Receiver name")
    recepteur_signature: Optional[str] = Field(None, max_length=500, description="Receiver signature (Base64 or path)")
    palette_ids: List[UUID] = Field(..., min_length=1, description="List of palette IDs delivered")
    date_depart: Optional[datetime] = None
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for reporting problems
class LivraisonDetailProbleme(BaseModel):
    """Schema for reporting delivery problems."""
    
    problemes: str = Field(..., min_length=1, max_length=1000, description="Description of problems")
    observations: Optional[str] = Field(None, max_length=1000)

