"""
Collecte Vide Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.palette import PaletteType


# Base schema with common attributes
class CollecteVideBase(BaseModel):
    """Base CollecteVide schema with common attributes."""
    
    bon_enlevement_id: UUID = Field(..., description="Foreign key to bons_enlevement")
    livraison_detail_id: Optional[UUID] = Field(None, description="Foreign key to livraisons_details (if multi-depot)")
    depot_id: Optional[UUID] = Field(None, description="Foreign key to depots (where collection occurred)")
    type_bouteille: PaletteType = Field(..., description="Bottle type (B6, B12, B28)")
    quantite_bouteilles_vides: int = Field(..., ge=0, description="Number of empty bottles")
    quantite_palettes_vides: int = Field(0, ge=0, description="Number of empty palette structures")
    collecteur_nom: Optional[str] = Field(None, max_length=255, description="Collector name (often driver)")
    observations: Optional[str] = Field(None, max_length=1000, description="Observations")


# Schema for creating a new CollecteVide
class CollecteVideCreate(CollecteVideBase):
    """Schema for creating a new CollecteVide."""
    
    date_collecte: Optional[datetime] = None


# Schema for updating an existing CollecteVide
class CollecteVideUpdate(BaseModel):
    """Schema for updating an existing CollecteVide (all fields optional)."""
    
    type_bouteille: Optional[PaletteType] = None
    quantite_bouteilles_vides: Optional[int] = Field(None, ge=0)
    quantite_palettes_vides: Optional[int] = Field(None, ge=0)
    collecteur_nom: Optional[str] = Field(None, max_length=255)
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for reading a CollecteVide (includes ID and timestamps)
class CollecteVideRead(CollecteVideBase):
    """Schema for reading a CollecteVide."""
    
    id: UUID
    date_collecte: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing CollecteVides (minimal info)
class CollecteVideList(BaseModel):
    """Schema for listing CollecteVides (minimal info)."""
    
    id: UUID
    bon_enlevement_id: UUID
    type_bouteille: PaletteType
    quantite_bouteilles_vides: int
    quantite_palettes_vides: int
    date_collecte: datetime
    
    class Config:
        from_attributes = True


# Schema with related data
class CollecteVideDetail(CollecteVideRead):
    """Schema for detailed CollecteVide with related data."""
    
    bon_enlevement_numero: Optional[str] = Field(None, description="Bon d'enlèvement numero")
    depot_name: Optional[str] = Field(None, description="Name of the depot")
    livraison_detail_ordre: Optional[int] = Field(None, description="Order of the livraison detail")
    total_items: Optional[int] = Field(None, description="Total items collected")
    
    class Config:
        from_attributes = True


# Schema for bulk collection
class CollecteVideBulk(BaseModel):
    """Schema for registering multiple collections at once."""
    
    bon_enlevement_id: UUID
    livraison_detail_id: Optional[UUID] = None
    depot_id: Optional[UUID] = None
    collecteur_nom: Optional[str] = Field(None, max_length=255)
    collections: list[dict] = Field(..., min_length=1, description="List of collections by bottle type")
    
    # Example: 
    # collections = [
    #     {"type_bouteille": "B6", "quantite_bouteilles_vides": 10, "quantite_palettes_vides": 1},
    #     {"type_bouteille": "B12", "quantite_bouteilles_vides": 20, "quantite_palettes_vides": 2}
    # ]

