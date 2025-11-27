"""
Detail Retour Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.detail_retour import DetailRetourType, DetailRetourEtat
from app.models.palette import PaletteType


# Base schema with common attributes
class DetailRetourBase(BaseModel):
    """Base DetailRetour schema with common attributes."""
    
    bon_reception_retour_id: UUID = Field(..., description="Foreign key to bons_reception_retour")
    type_detail: DetailRetourType = Field(..., description="Type of item")
    type_bouteille: Optional[PaletteType] = Field(None, description="Bottle type (B6, B12, B28)")
    quantite_prevue: int = Field(..., ge=0, description="Expected quantity")
    quantite_recue: int = Field(0, ge=0, description="Received quantity")
    quantite_acceptee: int = Field(0, ge=0, description="Accepted quantity")
    quantite_refusee: int = Field(0, ge=0, description="Refused quantity")
    etat: Optional[DetailRetourEtat] = Field(None, description="Condition state")
    observations: Optional[str] = Field(None, max_length=1000, description="Observations")
    motif_refus: Optional[str] = Field(None, max_length=500, description="Refusal reason")


# Schema for creating a new DetailRetour
class DetailRetourCreate(DetailRetourBase):
    """Schema for creating a new DetailRetour."""
    pass


# Schema for updating an existing DetailRetour
class DetailRetourUpdate(BaseModel):
    """Schema for updating an existing DetailRetour (all fields optional)."""
    
    quantite_recue: Optional[int] = Field(None, ge=0)
    quantite_acceptee: Optional[int] = Field(None, ge=0)
    quantite_refusee: Optional[int] = Field(None, ge=0)
    etat: Optional[DetailRetourEtat] = None
    observations: Optional[str] = Field(None, max_length=1000)
    motif_refus: Optional[str] = Field(None, max_length=500)


# Schema for reading a DetailRetour (includes ID and timestamps)
class DetailRetourRead(DetailRetourBase):
    """Schema for reading a DetailRetour."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing DetailRetours (minimal info)
class DetailRetourList(BaseModel):
    """Schema for listing DetailRetours (minimal info)."""
    
    id: UUID
    bon_reception_retour_id: UUID
    type_detail: DetailRetourType
    type_bouteille: Optional[PaletteType]
    quantite_recue: int
    quantite_acceptee: int
    quantite_refusee: int
    etat: Optional[DetailRetourEtat]
    
    class Config:
        from_attributes = True


# Schema with calculated data
class DetailRetourDetail(DetailRetourRead):
    """Schema for detailed DetailRetour with calculated data."""
    
    ecart_quantite: Optional[int] = Field(None, description="Quantity difference (received - expected)")
    taux_acceptation: Optional[float] = Field(None, description="Acceptance rate (%)")
    is_complete: Optional[bool] = Field(None, description="All received items processed")
    
    class Config:
        from_attributes = True


# Schema for quality control input
class DetailRetourControle(BaseModel):
    """Schema for quality control input on a detail."""
    
    quantite_recue: int = Field(..., ge=0, description="Received quantity")
    quantite_acceptee: int = Field(..., ge=0, description="Accepted quantity")
    quantite_refusee: int = Field(..., ge=0, description="Refused quantity")
    etat: DetailRetourEtat = Field(..., description="Condition state")
    observations: Optional[str] = Field(None, max_length=1000)
    motif_refus: Optional[str] = Field(None, max_length=500)


# Schema for bulk detail creation
class DetailRetourBulkCreate(BaseModel):
    """Schema for creating multiple details at once."""
    
    bon_reception_retour_id: UUID
    details: List[dict] = Field(..., min_length=1, description="List of detail items")
    
    # Example:
    # details = [
    #     {"type_detail": "PALETTE_VIDE", "type_bouteille": "B6", "quantite_prevue": 10},
    #     {"type_detail": "BOUTEILLE_VIDE", "type_bouteille": "B12", "quantite_prevue": 50},
    #     {"type_detail": "CONSIGNE", "quantite_prevue": 5}
    # ]

