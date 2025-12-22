"""
Bon d'Enlèvement Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.bon_enlevement import BonEnlevementStatus


# Base schema with common attributes
class BonEnlevementBase(BaseModel):
    """Base BonEnlevement schema with common attributes."""
    
    numero_bon: Optional[str] = Field(None, min_length=1, max_length=100, description="Unique number of the Bon d'Enlèvement (auto-generated if not provided)")
    reference: Optional[str] = Field(None, max_length=100, description="Internal reference")
    centre_remplisseur_id: UUID = Field(..., description="Foreign key to the CentreRemplisseur model")
    grossiste_id: UUID = Field(..., description="Foreign key to the Partner model (ordering grossiste)")
    depot_principal_id: UUID = Field(..., description="Foreign key to the Depot model (final destination)")
    vehicule_immatriculation: Optional[str] = Field(None, max_length=50, description="Vehicle registration number")
    chauffeur_nom: Optional[str] = Field(None, max_length=255, description="Name of the driver")
    chauffeur_societe: Optional[str] = Field(None, max_length=255, description="Company of the driver")
    chauffeur_phone: Optional[str] = Field(None, max_length=20, description="Phone number of the driver")
    date_heure_livraison: Optional[datetime] = Field(None, description="Scheduled delivery date and time")
    observations: Optional[str] = Field(None, max_length=1000, description="Additional observations")
    instructions_livraison: Optional[str] = Field(None, max_length=1000, description="Special delivery instructions")


# Schema for creating a new BonEnlevement
class BonEnlevementCreate(BonEnlevementBase):
    """Schema for creating a new BonEnlevement."""
    
    palette_ids: Optional[List[UUID]] = Field(None, description="Optional list of palette IDs to assign during creation")


# Schema for updating an existing BonEnlevement
class BonEnlevementUpdate(BaseModel):
    """Schema for updating an existing BonEnlevement (all fields optional)."""
    
    reference: Optional[str] = Field(None, max_length=100)
    vehicule_immatriculation: Optional[str] = Field(None, max_length=50)
    chauffeur_nom: Optional[str] = Field(None, max_length=255)
    chauffeur_societe: Optional[str] = Field(None, max_length=255)
    chauffeur_phone: Optional[str] = Field(None, max_length=20)
    date_heure_livraison: Optional[datetime] = Field(None, description="Scheduled delivery date and time")
    observations: Optional[str] = Field(None, max_length=1000)
    instructions_livraison: Optional[str] = Field(None, max_length=1000)


# Schema for reading a BonEnlevement (includes ID and timestamps)
class BonEnlevementRead(BonEnlevementBase):
    """Schema for reading a BonEnlevement."""
    
    id: UUID
    status: BonEnlevementStatus
    date_creation: datetime
    date_validation: Optional[datetime]
    date_chargement: Optional[datetime]
    date_depart: Optional[datetime]
    date_arrivee_finale: Optional[datetime]
    validateur_centre_id: Optional[UUID]
    recepteur_final_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing BonEnlevements (minimal info)
class BonEnlevementList(BaseModel):
    """Schema for listing BonEnlevements (minimal info)."""
    
    id: UUID
    numero_bon: str
    status: BonEnlevementStatus
    centre_remplisseur_id: UUID
    grossiste_id: UUID
    date_creation: datetime
    date_depart: Optional[datetime]
    chauffeur_nom: Optional[str]
    
    class Config:
        from_attributes = True


# Schema with related data
class BonEnlevementDetail(BonEnlevementRead):
    """Schema for detailed BonEnlevement with related data."""
    
    centre_remplisseur_name: Optional[str] = Field(None, description="Name of the filling center")
    grossiste_name: Optional[str] = Field(None, description="Name of the grossiste")
    depot_principal_name: Optional[str] = Field(None, description="Name of the main depot")
    palettes_count: Optional[int] = Field(None, description="Number of palettes")
    livraisons_count: Optional[int] = Field(None, description="Number of delivery stops")
    collectes_count: Optional[int] = Field(None, description="Number of empty collections")
    
    class Config:
        from_attributes = True


# Schema for status updates
class BonEnlevementStatusUpdate(BaseModel):
    """Schema for updating BonEnlevement status."""
    
    status: BonEnlevementStatus
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for validation
class BonEnlevementValidation(BaseModel):
    """Schema for validating a BonEnlevement."""
    
    validateur_centre_id: UUID
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for loading
class BonEnlevementChargement(BaseModel):
    """Schema for starting loading of a BonEnlevement."""
    
    palette_ids: List[UUID] = Field(..., min_length=1, description="List of palette IDs to load")
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for departure
class BonEnlevementDepart(BaseModel):
    """Schema for departure of a BonEnlevement."""
    
    date_depart: Optional[datetime] = None
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for final reception
class BonEnlevementReception(BaseModel):
    """Schema for final reception of a BonEnlevement."""
    
    recepteur_final_id: UUID
    date_arrivee_finale: Optional[datetime] = None
    observations: Optional[str] = Field(None, max_length=1000)
    otp_code: Optional[str] = Field(None, max_length=10, description="OTP for validation")

