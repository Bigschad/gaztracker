"""
Centres Remplisseurs API Routes

CRUD endpoints for CentreRemplisseur management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.services.centre_remplisseur_service import CentreRemplisseurService
from app.schemas.centre_remplisseur import (
    CentreRemplisseurCreate,
    CentreRemplisseurUpdate,
    CentreRemplisseurRead,
    CentreRemplisseurList,
    CentreRemplisseurDetail
)
from app.core.exceptions import NotFoundException, DuplicateException


router = APIRouter()


@router.post("/", response_model=CentreRemplisseurRead, status_code=status.HTTP_201_CREATED)
def create_centre(
    schema: CentreRemplisseurCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new Centre Remplisseur.
    
    - **name**: Name of the filling center
    - **code**: Unique code
    - **grand_distributeur_id**: ID of the parent grand distributeur
    - **address**, **city**, **postal_code**: Location details
    - **latitude**, **longitude**: GPS coordinates (optional)
    - **contact_name**, **contact_phone**: Contact person
    """
    try:
        centre = CentreRemplisseurService.create(db, schema)
        return centre
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[CentreRemplisseurList])
def list_centres(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    grand_distributeur_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all Centres Remplisseurs with optional filtering.
    
    - **grand_distributeur_id**: Filter by grand distributeur
    - **is_active**: Filter by active status
    - **city**: Filter by city
    - **search**: Search by name or code
    """
    centres = CentreRemplisseurService.get_all(
        db, 
        skip=skip, 
        limit=limit, 
        grand_distributeur_id=grand_distributeur_id,
        is_active=is_active,
        city=city,
        search=search
    )
    return centres


@router.get("/nearby")
def get_nearby_centres(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    db: Session = Depends(get_sync_db)
):
    """
    Get centres near a GPS location.
    
    - **latitude**: Search latitude
    - **longitude**: Search longitude
    - **radius_km**: Search radius in kilometers (default: 10km)
    """
    centres = CentreRemplisseurService.get_by_location(db, latitude, longitude, radius_km)
    return centres


@router.get("/{centre_id}", response_model=CentreRemplisseurDetail)
def get_centre(
    centre_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Get a Centre Remplisseur by ID with statistics."""
    try:
        stats = CentreRemplisseurService.get_with_stats(db, centre_id)
        
        centre = stats["centre_remplisseur"]
        return CentreRemplisseurDetail(
            **{
                "id": centre.id,
                "name": centre.name,
                "code": centre.code,
                "grand_distributeur_id": centre.grand_distributeur_id,
                "address": centre.address,
                "city": centre.city,
                "postal_code": centre.postal_code,
                "country": centre.country,
                "phone": centre.phone,
                "email": centre.email,
                "contact_name": centre.contact_name,
                "contact_phone": centre.contact_phone,
                "is_active": centre.is_active,
                "latitude": centre.latitude,
                "longitude": centre.longitude,
                "notes": centre.notes,
                "created_at": centre.created_at,
                "updated_at": centre.updated_at,
                "grand_distributeur_name": stats["grand_distributeur_name"],
                "groupe_name": stats["groupe_name"],
                "bons_enlevement_count": stats["bons_enlevement_count"],
                "bons_retour_count": stats["bons_retour_count"]
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{centre_id}", response_model=CentreRemplisseurRead)
def update_centre(
    centre_id: UUID,
    schema: CentreRemplisseurUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update a Centre Remplisseur."""
    try:
        centre = CentreRemplisseurService.update(db, centre_id, schema)
        return centre
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{centre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_centre(
    centre_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Delete a Centre Remplisseur."""
    try:
        CentreRemplisseurService.delete(db, centre_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{centre_id}/activate", response_model=CentreRemplisseurRead)
def activate_centre(
    centre_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Activate a Centre Remplisseur."""
    try:
        centre = CentreRemplisseurService.activate(db, centre_id)
        return centre
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{centre_id}/deactivate", response_model=CentreRemplisseurRead)
def deactivate_centre(
    centre_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Deactivate a Centre Remplisseur."""
    try:
        centre = CentreRemplisseurService.deactivate(db, centre_id)
        return centre
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

