"""
Dépôts API Routes

CRUD endpoints for Depot management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.services.depot_service import DepotService
from app.schemas.depot import (
    DepotCreate,
    DepotUpdate,
    DepotRead,
    DepotList,
    DepotDetail,
    DepotLocation
)
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


router = APIRouter()


@router.post("/", response_model=DepotRead, status_code=status.HTTP_201_CREATED)
def create_depot(
    schema: DepotCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new Depot.
    
    - **name**: Name of the depot
    - **code**: Unique code (optional)
    - **partner_id**: ID of the partner (grossiste or revendeur)
    - **address**, **city**: Location
    - **latitude**, **longitude**: GPS coordinates (optional)
    - **capacity_b28**, **capacity_b12**, **capacity_b6**: Capacities per type
    - **is_main_depot**: Whether this is the main depot for the partner
    """
    try:
        depot = DepotService.create(db, schema)
        return depot
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[DepotList])
def list_depots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    partner_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    is_main_depot: Optional[bool] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all Depots with optional filtering.
    
    - **partner_id**: Filter by partner
    - **is_active**: Filter by active status
    - **is_main_depot**: Filter by main depot status
    - **city**: Filter by city
    - **search**: Search by name or code
    """
    depots = DepotService.get_all(
        db,
        skip=skip,
        limit=limit,
        partner_id=partner_id,
        is_active=is_active,
        is_main_depot=is_main_depot,
        city=city,
        search=search
    )
    return depots


@router.get("/locations", response_model=List[DepotLocation])
def get_depot_locations(
    is_active: bool = True,
    db: Session = Depends(get_sync_db)
):
    """
    Get depot locations for map display.
    
    Returns only depots with GPS coordinates.
    """
    depots = DepotService.get_all(db, is_active=is_active, limit=1000)
    # Filter only depots with coordinates
    locations = [
        DepotLocation(
            id=d.id,
            name=d.name,
            latitude=d.latitude,
            longitude=d.longitude,
            address=d.address,
            city=d.city
        )
        for d in depots if d.latitude and d.longitude
    ]
    return locations


@router.get("/nearby")
def get_nearby_depots(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    is_active: bool = True,
    db: Session = Depends(get_sync_db)
):
    """
    Get depots near a GPS location.
    
    - **latitude**: Search latitude
    - **longitude**: Search longitude
    - **radius_km**: Search radius in kilometers
    - **is_active**: Filter by active status
    """
    depots = DepotService.get_by_location(db, latitude, longitude, radius_km, is_active)
    return depots


@router.get("/{depot_id}", response_model=DepotDetail)
def get_depot(
    depot_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Get a Depot by ID with statistics."""
    try:
        stats = DepotService.get_with_stats(db, depot_id)
        
        depot = stats["depot"]
        return DepotDetail(
            **{
                "id": depot.id,
                "name": depot.name,
                "code": depot.code,
                "partner_id": depot.partner_id,
                "address": depot.address,
                "city": depot.city,
                "postal_code": depot.postal_code,
                "latitude": depot.latitude,
                "longitude": depot.longitude,
                "contact_name": depot.contact_name,
                "contact_phone": depot.contact_phone,
                "capacity_b28": depot.capacity_b28,
                "capacity_b12": depot.capacity_b12,
                "capacity_b6": depot.capacity_b6,
                "is_active": depot.is_active,
                "is_main_depot": depot.is_main_depot,
                "notes": depot.notes,
                "created_at": depot.created_at,
                "updated_at": depot.updated_at,
                "partner_name": stats["partner_name"],
                "partner_type": stats["partner_type"],
                "total_capacity": stats["total_capacity"],
                "palettes_count": stats["palettes_count"]
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{depot_id}", response_model=DepotRead)
def update_depot(
    depot_id: UUID,
    schema: DepotUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update a Depot."""
    try:
        depot = DepotService.update(db, depot_id, schema)
        return depot
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{depot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_depot(
    depot_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Delete a Depot."""
    try:
        DepotService.delete(db, depot_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{depot_id}/activate", response_model=DepotRead)
def activate_depot(
    depot_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Activate a Depot."""
    try:
        depot = DepotService.activate(db, depot_id)
        return depot
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{depot_id}/deactivate", response_model=DepotRead)
def deactivate_depot(
    depot_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Deactivate a Depot."""
    try:
        depot = DepotService.deactivate(db, depot_id)
        return depot
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{depot_id}/set-main", response_model=DepotRead)
def set_as_main_depot(
    depot_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """
    Set this depot as the main depot for its partner.
    
    Will unset any existing main depot for the same partner.
    """
    try:
        depot = DepotService.set_as_main(db, depot_id)
        return depot
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

