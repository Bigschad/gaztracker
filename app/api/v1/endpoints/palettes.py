"""
Palettes API Routes

CRUD endpoints for Palette management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.models.user import User
from app.models.palette import PaletteType, PaletteStatus
from app.schemas.palette import (
    PaletteCreate,
    PaletteUpdate,
    PaletteResponse,
    PaletteListResponse,
    PaletteDetailResponse,
    PaletteLocationUpdate,
    PaletteScanRequest,
    PaletteScanResponse,
    PaletteStatistics
)
from app.services.palette_service import PaletteService
from app.middleware.auth_middleware import get_current_user_sync
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()


@router.get("/next-code", response_model=dict)
def get_next_code(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Get the next available palette reference code.
    
    Returns:
        Dictionary with the next code
    """
    code = PaletteService._generate_reference_code(db)
    return {"code": code}


@router.post("/", response_model=PaletteResponse, status_code=status.HTTP_201_CREATED)
def create_palette(
    palette: PaletteCreate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Create a new palette.
    """
    return PaletteService.create_palette(db, palette, current_user)


@router.get("/{palette_id}", response_model=PaletteResponse)
def get_palette(
    palette_id: UUID,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Get a palette by ID.
    """
    return PaletteService.get_palette(db, palette_id)


@router.get("/", response_model=PaletteListResponse)
def list_palettes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[PaletteType] = None,
    status: Optional[PaletteStatus] = None,
    current_centre_remplisseur_id: Optional[UUID] = Query(None, description="Filter by current centre remplisseur ID"),
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    List palettes with filtering and pagination.
    """
    items, total = PaletteService.list_palettes(
        db,
        palette_type=type,
        status=status,
        current_centre_remplisseur_id=current_centre_remplisseur_id,
        search=search,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaletteListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.patch("/{palette_id}", response_model=PaletteResponse)
def update_palette(
    palette_id: UUID,
    palette_update: PaletteUpdate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Update a palette.
    """
    return PaletteService.update_palette(db, palette_id, palette_update, current_user)


@router.post("/{palette_id}/location", response_model=PaletteResponse)
def update_palette_location(
    palette_id: UUID,
    location: PaletteLocationUpdate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Update palette location.
    """
    return PaletteService.update_palette_location(db, palette_id, location, current_user)


@router.post("/scan", response_model=PaletteScanResponse)
def scan_palette(
    scan_request: PaletteScanRequest,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Scan a palette by RFID tag.
    """
    palette = PaletteService.scan_palette(
        db,
        scan_request.rfid_tag,
        current_user,
        latitude=scan_request.latitude,
        longitude=scan_request.longitude,
        notes=scan_request.notes
    )
    
    return PaletteScanResponse(
        success=True,
        message="Palette scannée avec succès",
        palette=palette
    )


@router.get("/stats/overview", response_model=PaletteStatistics)
def get_palette_statistics(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Get palette statistics.
    """
    return PaletteService.get_palette_statistics(db)

