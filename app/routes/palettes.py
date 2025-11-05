"""
Palette Routes

API endpoints for palette management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import logging

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User, UserRole
from app.models.palette import PaletteType, PaletteStatus
from app.schemas.palette import (
    PaletteCreate,
    PaletteUpdate,
    PaletteLocationUpdate,
    PaletteResponse,
    PaletteListResponse,
    PaletteScanRequest,
    PaletteScanResponse,
    PaletteStatistics,
)
from app.services.palette_service import PaletteService
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    InvalidStatusTransitionException,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=PaletteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new palette",
    description="""
    Create a new palette and attach an RFID tag.

    **Authorized roles**: ADMIN, OPERATEUR_USINE

    **Process:**
    1. Verify RFID tag exists and is NOT_ASSIGNED
    2. Create palette with status CREATION
    3. Assign RFID tag (status changes to ASSIGNED)
    4. Create initial movement history entry

    **Requirements:**
    - RFID tag must exist and be NOT_ASSIGNED
    - RFID tag must be active
    """,
    responses={
        201: {"description": "Palette created successfully"},
        400: {"description": "Invalid data or tag not available"},
        401: {"description": "Unauthorized"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "RFID tag not found"},
    },
)
async def create_palette(
    palette_create: PaletteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new palette."""
    try:
        # Verify permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.OPERATEUR_USINE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN or OPERATEUR_USINE can create palettes",
            )

        palette = PaletteService.create_palette(db, palette_create, current_user)
        return palette

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating palette: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{palette_id}",
    response_model=PaletteResponse,
    summary="Get palette by ID",
    description="Retrieve detailed information about a specific palette including RFID tag details.",
    responses={
        200: {"description": "Palette found"},
        404: {"description": "Palette not found"},
    },
)
async def get_palette(
    palette_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a palette by ID."""
    try:
        palette = PaletteService.get_palette(db, palette_id, include_relations=True)
        return palette

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving palette: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/rfid/{rfid_tag_number}",
    response_model=PaletteResponse,
    summary="Get palette by RFID tag number",
    description="Retrieve palette by scanning its RFID tag number. Useful for mobile scanning operations.",
    responses={
        200: {"description": "Palette found"},
        404: {"description": "Palette not found"},
    },
)
async def get_palette_by_rfid(
    rfid_tag_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a palette by its RFID tag number."""
    try:
        palette = PaletteService.get_palette_by_rfid(db, rfid_tag_number)
        return palette

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving palette by RFID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/",
    response_model=PaletteListResponse,
    summary="List palettes",
    description="""
    List all palettes with optional filters and pagination.

    **Filters:**
    - type: Filter by palette type (B6, B12, B28)
    - status: Filter by status (CREATION, EN_STOCK, EN_ROUTE, etc.)
    - created_by_id: Filter by creator user ID
    - search: Search in RFID tag number or notes
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    """,
)
async def list_palettes(
    type: Optional[PaletteType] = Query(None, description="Filter by palette type"),
    status: Optional[PaletteStatus] = Query(None, description="Filter by status"),
    created_by_id: Optional[UUID] = Query(None, description="Filter by creator"),
    search: Optional[str] = Query(None, description="Search in RFID or notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List palettes with filters and pagination."""
    try:
        palettes, total = PaletteService.list_palettes(
            db,
            palette_type=type,
            status=status,
            created_by_id=created_by_id,
            search=search,
            page=page,
            page_size=page_size,
        )

        return PaletteListResponse(
            total=total,
            page=page,
            page_size=page_size,
            palettes=palettes,
        )

    except Exception as e:
        logger.error(f"Error listing palettes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{palette_id}",
    response_model=PaletteResponse,
    summary="Update palette",
    description="""
    Update palette information (status, location, notes, etc.).

    **Common use cases:**
    - Change status (e.g., CREATION → EN_STOCK)
    - Update location coordinates
    - Add notes

    **Note**: Status transitions are validated. Not all transitions are allowed.
    A movement history entry is created when status changes.
    """,
    responses={
        200: {"description": "Palette updated successfully"},
        400: {"description": "Invalid status transition"},
        404: {"description": "Palette not found"},
    },
)
async def update_palette(
    palette_id: UUID,
    palette_update: PaletteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a palette."""
    try:
        palette = PaletteService.update_palette(
            db, palette_id, palette_update, current_user
        )
        return palette

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (ValidationException, InvalidStatusTransitionException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating palette: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{palette_id}/location",
    response_model=PaletteResponse,
    summary="Update palette location",
    description="""
    Update palette GPS location and optional address.

    Creates a movement history entry with the new location.
    Useful for tracking palette position during transit.
    """,
    responses={
        200: {"description": "Location updated successfully"},
        404: {"description": "Palette not found"},
    },
)
async def update_palette_location(
    palette_id: UUID,
    location_update: PaletteLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update palette location."""
    try:
        palette = PaletteService.update_palette_location(
            db, palette_id, location_update, current_user
        )
        return palette

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating palette location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{palette_id}/history",
    summary="Get palette movement history",
    description="""
    Retrieve complete movement history for a palette.

    Returns chronologically ordered list of all movements including:
    - Creation
    - Status changes
    - Location updates
    - Scans
    """,
    responses={
        200: {"description": "History retrieved successfully"},
        404: {"description": "Palette not found"},
    },
)
async def get_palette_history(
    palette_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete movement history for a palette."""
    try:
        movements = PaletteService.get_palette_history(db, palette_id)

        return {
            "palette_id": str(palette_id),
            "total_movements": len(movements),
            "movements": movements,
        }

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving palette history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/scan",
    response_model=PaletteScanResponse,
    summary="Scan a palette",
    description="""
    Scan a palette by RFID tag and record the scan event.

    **Use cases:**
    - Factory exit scan
    - Arrival at distributor
    - Return to factory
    - Any checkpoint scan

    Creates a movement history entry with scan timestamp and location.
    """,
    responses={
        200: {"description": "Palette scanned successfully"},
        404: {"description": "Palette not found"},
    },
)
async def scan_palette(
    scan_request: PaletteScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan a palette by RFID."""
    try:
        palette = PaletteService.scan_palette(
            db,
            rfid_tag_number=scan_request.rfid_tag,
            current_user=current_user,
            latitude=scan_request.latitude,
            longitude=scan_request.longitude,
            notes=scan_request.notes,
        )

        return PaletteScanResponse(
            success=True,
            message=f"Palette {palette.id} scanned successfully",
            palette=palette,
        )

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error scanning palette: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/statistics/summary",
    response_model=PaletteStatistics,
    summary="Get palette statistics",
    description="Get aggregated statistics about all palettes in the system.",
)
async def get_palette_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get palette statistics."""
    try:
        stats = PaletteService.get_palette_statistics(db)
        return PaletteStatistics(**stats)

    except Exception as e:
        logger.error(f"Error getting palette statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
