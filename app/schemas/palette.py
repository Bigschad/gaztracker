"""
Palette Schemas

Pydantic schemas for Palette model validation and serialization.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.palette import PaletteType, PaletteStatus, PaletteCondition
from app.schemas.rfid_tag import RFIDTagResponse
from app.schemas.centre_remplisseur import CentreRemplisseurRead


# =============================================================================
# Base Schemas
# =============================================================================

class PaletteBase(BaseModel):
    """Base palette schema with common fields."""

    type: PaletteType = Field(..., description="Type of gas bottles (B6, B12, B28)")
    condition: Optional[PaletteCondition] = Field(None, description="Condition de la palette (NEUVE ou RECONDITIONNEE)")
    reference_code: Optional[str] = Field(None, max_length=50, description="Code de référence personnalisé")
    capacity: Optional[int] = Field(None, ge=1, description="Capacité en nombre de bouteilles possibles")
    manufacturing_date: Optional[date] = Field(None, description="Date de fabrication")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


# =============================================================================
# Request Schemas
# =============================================================================

class PaletteCreate(PaletteBase):
    """Schema for creating a new palette."""

    rfid_tag_id: Optional[UUID] = Field(None, description="ID of the RFID tag to attach (must be NOT_ASSIGNED). Can be added later.")
    current_partner_id: Optional[UUID] = Field(None, description="ID du partenaire (grossiste) chez qui se trouve la palette")
    current_centre_remplisseur_id: Optional[UUID] = Field(None, description="ID du centre remplisseur où se trouve la palette")
    location_latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    location_longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    location_address: Optional[str] = Field(None, max_length=500, description="Physical address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "B12",
                "rfid_tag_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_latitude": 48.8566,
                "location_longitude": 2.3522,
                "notes": "Lot de bouteilles standard"
            }
        }
    )


class PaletteUpdate(BaseModel):
    """Schema for updating an existing palette."""

    type: Optional[PaletteType] = Field(None, description="Type of gas bottles")
    condition: Optional[PaletteCondition] = Field(None, description="Condition de la palette (NEUVE ou RECONDITIONNEE)")
    reference_code: Optional[str] = Field(None, max_length=50, description="Code de référence personnalisé")
    capacity: Optional[int] = Field(None, ge=1, description="Capacité en nombre de bouteilles possibles")
    manufacturing_date: Optional[date] = Field(None, description="Date de fabrication")
    status: Optional[PaletteStatus] = Field(None, description="Palette status")
    rfid_tag_id: Optional[UUID] = Field(None, description="ID of new RFID tag to assign (must be NOT_ASSIGNED)")
    current_partner_id: Optional[UUID] = Field(None, description="ID du partenaire (grossiste) chez qui se trouve la palette")
    current_centre_remplisseur_id: Optional[UUID] = Field(None, description="ID du centre remplisseur où se trouve la palette")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    location_latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    location_longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    location_address: Optional[str] = Field(None, max_length=500, description="Physical address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "AU_DEPOT",
                "notes": "Palette vérifiée et prête"
            }
        }
    )


class PaletteLocationUpdate(BaseModel):
    """Schema for updating palette location."""

    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    address: Optional[str] = Field(None, max_length=500, description="Physical address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "address": "Paris, France"
            }
        }
    )


class PaletteScanRequest(BaseModel):
    """Schema for scanning a palette."""

    rfid_tag: str = Field(..., max_length=50, description="RFID tag to scan")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    notes: Optional[str] = Field(None, max_length=1000, description="Scan notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rfid_tag": "GAZ123456789",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "notes": "Scan à l'arrivée"
            }
        }
    )


# =============================================================================
# Response Schemas
# =============================================================================

class PaletteResponse(PaletteBase):
    """Schema for palette response."""

    id: UUID = Field(..., description="Palette ID")
    serial_number: str = Field(..., description="Human-readable serial number (e.g., PAL-2025-00001)")
    rfid_tag_id: Optional[UUID] = Field(None, description="RFID tag ID")
    rfid_tag: Optional[RFIDTagResponse] = Field(None, description="RFID tag details")
    status: PaletteStatus = Field(..., description="Current status")
    condition: Optional[PaletteCondition] = Field(None, description="Condition de la palette (NEUVE ou RECONDITIONNEE)")
    is_full: bool = Field(..., description="Whether the palette is full")
    current_partner_id: Optional[UUID] = Field(None, description="Current partner (grossiste) ID")
    current_centre_remplisseur_id: Optional[UUID] = Field(None, description="Current centre remplisseur ID")
    current_centre_remplisseur: Optional[CentreRemplisseurRead] = Field(None, description="Current centre remplisseur details")
    bon_enlevement_actuel_id: Optional[UUID] = Field(None, description="Current bon d'enlèvement ID")
    location_latitude: Optional[float] = Field(None, description="GPS latitude")
    location_longitude: Optional[float] = Field(None, description="GPS longitude")
    location_address: Optional[str] = Field(None, description="Physical address")
    created_by_id: Optional[UUID] = Field(None, description="Creator user ID")
    current_expedition_id: Optional[UUID] = Field(None, description="Current expedition ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "serial_number": "PAL-2025-00001",
                "rfid_tag_id": "550e8400-e29b-41d4-a716-446655440000",
                "rfid_tag": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "tag_number": "RFID-2024-001",
                    "status": "ASSIGNED",
                    "created_by_id": "123e4567-e89b-12d3-a456-426614174000",
                    "is_active": True,
                    "notes": None,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:35:00Z",
                    "assigned_at": "2024-01-15T10:35:00Z"
                },
                "type": "B12",
                "status": "AU_DEPOT",
                "location_latitude": 48.8566,
                "location_longitude": 2.3522,
                "location_address": "Usine principale, Paris",
                "notes": "Lot de bouteilles standard",
                "created_by_id": "123e4567-e89b-12d3-a456-426614174001",
                "current_expedition_id": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class PaletteDetailResponse(PaletteResponse):
    """Schema for detailed palette response with movements."""

    # Will be enhanced in future phases with movement history
    pass


class PaletteListResponse(BaseModel):
    """Schema for paginated palette list response."""

    items: list[PaletteResponse] = Field(..., description="List of palettes")
    total: int = Field(..., description="Total number of palettes")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 500,
                "page": 1,
                "page_size": 20,
                "palettes": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "serial_number": "PAL-2025-00001",
                        "rfid_tag": "GAZ123456789",
                        "type": "B12",
                        "status": "AU_DEPOT",
                        "location_latitude": 48.8566,
                        "location_longitude": 2.3522,
                        "location_address": "Usine principale",
                        "notes": None,
                        "created_by_id": "123e4567-e89b-12d3-a456-426614174001",
                        "current_expedition_id": None,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }
    )


class PaletteScanResponse(BaseModel):
    """Schema for palette scan response."""

    success: bool = Field(..., description="Scan success status")
    message: str = Field(..., description="Response message")
    palette: PaletteResponse = Field(..., description="Scanned palette information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Palette scannée avec succès",
                "palette": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "serial_number": "PAL-2025-00001",
                    "rfid_tag": "GAZ123456789",
                    "type": "B12",
                    "status": "EN_ROUTE_LIVRAISON",
                    "location_latitude": 48.8566,
                    "location_longitude": 2.3522,
                    "location_address": None,
                    "notes": None,
                    "created_by_id": "123e4567-e89b-12d3-a456-426614174001",
                    "current_expedition_id": "123e4567-e89b-12d3-a456-426614174002",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T11:00:00Z"
                }
            }
        }
    )


# =============================================================================
# Statistics & Summary Schemas
# =============================================================================

class PaletteStatistics(BaseModel):
    """Schema for palette statistics."""

    total_palettes: int = Field(..., description="Total number of palettes")
    by_type: dict[str, int] = Field(..., description="Count by palette type")
    by_status: dict[str, int] = Field(..., description="Count by status")
    in_stock: int = Field(..., description="Palettes in stock")
    in_transit: int = Field(..., description="Palettes in transit")
    delivered: int = Field(..., description="Palettes delivered")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_palettes": 500,
                "by_type": {
                    "B6": 150,
                    "B12": 250,
                    "B28": 100
                },
                "by_status": {
                    "AU_DEPOT": 200,
                    "AU_CENTRE": 100,
                    "EN_ROUTE_LIVRAISON": 150,
                    "EN_ROUTE_RETOUR": 50
                },
                "in_stock": 300,
                "in_transit": 150,
                "delivered": 50
            }
        }
    )
