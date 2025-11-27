"""
Bon de Réception Retour Pydantic Schemas

Schemas for request/response validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.bon_reception_retour import BonReceptionRetourStatus


# Base schema with common attributes
class BonReceptionRetourBase(BaseModel):
    """Base BonReceptionRetour schema with common attributes."""
    
    numero_bl: str = Field(..., min_length=1, max_length=100, description="BL number")
    numero_reception: str = Field(..., min_length=1, max_length=100, description="Reception number")
    grossiste_id: UUID = Field(..., description="Foreign key to partners")
    depot_depart_id: UUID = Field(..., description="Foreign key to depots")
    centre_remplisseur_id: UUID = Field(..., description="Foreign key to centres_remplisseurs")
    vehicule_immatriculation: Optional[str] = Field(None, max_length=50, description="Vehicle registration")
    transporteur_nom: Optional[str] = Field(None, max_length=255, description="Transporter name")
    transporteur_societe: Optional[str] = Field(None, max_length=255, description="Transporter company")
    observations: Optional[str] = Field(None, max_length=1000, description="Observations")


# Schema for creating a new BonReceptionRetour
class BonReceptionRetourCreate(BonReceptionRetourBase):
    """Schema for creating a new BonReceptionRetour."""
    pass


# Schema for updating an existing BonReceptionRetour
class BonReceptionRetourUpdate(BaseModel):
    """Schema for updating an existing BonReceptionRetour (all fields optional)."""
    
    vehicule_immatriculation: Optional[str] = Field(None, max_length=50)
    transporteur_nom: Optional[str] = Field(None, max_length=255)
    transporteur_societe: Optional[str] = Field(None, max_length=255)
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for reading a BonReceptionRetour (includes ID and timestamps)
class BonReceptionRetourRead(BonReceptionRetourBase):
    """Schema for reading a BonReceptionRetour."""
    
    id: UUID
    status: BonReceptionRetourStatus
    date_creation: datetime
    date_depart: Optional[datetime]
    date_arrivee: Optional[datetime]
    date_controle: Optional[datetime]
    date_validation: Optional[datetime]
    controleur_id: Optional[UUID]
    magasinier_id: Optional[UUID]
    manquants: Optional[str]
    client_signature: Optional[str]
    magasinier_signature: Optional[str]
    controleur_signature: Optional[str]
    palette_count: int
    palette_acceptees: int
    palette_refusees: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for listing BonReceptionRetours (minimal info)
class BonReceptionRetourList(BaseModel):
    """Schema for listing BonReceptionRetours (minimal info)."""
    
    id: UUID
    numero_bl: str
    numero_reception: str
    status: BonReceptionRetourStatus
    grossiste_id: UUID
    centre_remplisseur_id: UUID
    date_creation: datetime
    date_arrivee: Optional[datetime]
    palette_count: int
    
    class Config:
        from_attributes = True


# Schema with related data
class BonReceptionRetourDetail(BonReceptionRetourRead):
    """Schema for detailed BonReceptionRetour with related data."""
    
    grossiste_name: Optional[str] = Field(None, description="Name of the grossiste")
    depot_depart_name: Optional[str] = Field(None, description="Name of the departure depot")
    centre_remplisseur_name: Optional[str] = Field(None, description="Name of the filling center")
    controleur_name: Optional[str] = Field(None, description="Name of the quality controller")
    magasinier_name: Optional[str] = Field(None, description="Name of the warehouse keeper")
    details_count: Optional[int] = Field(None, description="Number of detail lines")
    taux_acceptation: Optional[float] = Field(None, description="Acceptance rate (%)")
    
    class Config:
        from_attributes = True


# Schema for status updates
class BonReceptionRetourStatusUpdate(BaseModel):
    """Schema for updating BonReceptionRetour status."""
    
    status: BonReceptionRetourStatus
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for departure
class BonReceptionRetourDepart(BaseModel):
    """Schema for departure from depot."""
    
    date_depart: Optional[datetime] = None
    palette_ids: List[UUID] = Field(..., min_length=1, description="List of palette IDs being returned")
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for arrival
class BonReceptionRetourArrivee(BaseModel):
    """Schema for arrival at filling center."""
    
    magasinier_id: UUID = Field(..., description="Warehouse keeper ID")
    date_arrivee: Optional[datetime] = None
    observations: Optional[str] = Field(None, max_length=1000)
    magasinier_signature: Optional[str] = Field(None, max_length=500)


# Schema for quality control
class BonReceptionRetourControle(BaseModel):
    """Schema for quality control."""
    
    controleur_id: UUID = Field(..., description="Quality controller ID")
    date_controle: Optional[datetime] = None
    details: List[dict] = Field(..., min_length=1, description="List of control details")
    manquants: Optional[str] = Field(None, max_length=1000)
    observations: Optional[str] = Field(None, max_length=1000)
    controleur_signature: Optional[str] = Field(None, max_length=500)
    
    # Example:
    # details = [
    #     {"type_detail": "PALETTE_VIDE", "type_bouteille": "B6", "quantite_prevue": 10, 
    #      "quantite_recue": 9, "quantite_acceptee": 8, "quantite_refusee": 1, "etat": "BON"},
    #     ...
    # ]


# Schema for validation
class BonReceptionRetourValidation(BaseModel):
    """Schema for final validation."""
    
    date_validation: Optional[datetime] = None
    client_signature: Optional[str] = Field(None, max_length=500)
    observations: Optional[str] = Field(None, max_length=1000)


# Schema for refusal
class BonReceptionRetourRefus(BaseModel):
    """Schema for refusal."""
    
    motif_refus: str = Field(..., min_length=1, max_length=1000, description="Refusal reason")
    observations: Optional[str] = Field(None, max_length=1000)

