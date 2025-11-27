"""
Groupes API Routes

CRUD endpoints for Groupe management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.services.groupe_service import GroupeService
from app.schemas.groupe import (
    GroupeCreate,
    GroupeUpdate,
    GroupeRead,
    GroupeList,
    GroupeDetail
)
from app.core.exceptions import NotFoundException, DuplicateException


router = APIRouter()


@router.post("/", response_model=GroupeRead, status_code=status.HTTP_201_CREATED)
def create_groupe(
    schema: GroupeCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new Groupe.
    
    - **name**: Name of the group
    - **code**: Unique code for the group
    - **address**: Physical address (optional)
    - **city**: City (optional)
    - **phone**: Phone number (optional)
    - **email**: Email address (optional)
    - **is_active**: Active status (default: true)
    - **notes**: Additional notes (optional)
    """
    try:
        groupe = GroupeService.create(db, schema)
        return groupe
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[GroupeList])
def list_groupes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all Groupes with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status
    - **search**: Search by name or code
    """
    groupes = GroupeService.get_all(db, skip=skip, limit=limit, is_active=is_active, search=search)
    return groupes


@router.get("/count")
def count_groupes(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_sync_db)
):
    """
    Count Groupes with optional filtering.
    
    - **is_active**: Filter by active status
    """
    count = GroupeService.count(db, is_active=is_active)
    return {"count": count}


@router.get("/{groupe_id}", response_model=GroupeDetail)
def get_groupe(
    groupe_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """
    Get a Groupe by ID with statistics.
    
    Returns the groupe with count of grand distributeurs.
    """
    try:
        stats = GroupeService.get_with_stats(db, groupe_id)
        
        # Build response
        groupe = stats["groupe"]
        return GroupeDetail(
            **{
                "id": groupe.id,
                "name": groupe.name,
                "code": groupe.code,
                "address": groupe.address,
                "city": groupe.city,
                "phone": groupe.phone,
                "email": groupe.email,
                "is_active": groupe.is_active,
                "notes": groupe.notes,
                "created_at": groupe.created_at,
                "updated_at": groupe.updated_at,
                "grand_distributeurs_count": stats["grand_distributeurs_count"]
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{groupe_id}", response_model=GroupeRead)
def update_groupe(
    groupe_id: UUID,
    schema: GroupeUpdate,
    db: Session = Depends(get_sync_db)
):
    """
    Update a Groupe.
    
    Only provided fields will be updated.
    """
    try:
        groupe = GroupeService.update(db, groupe_id, schema)
        return groupe
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{groupe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_groupe(
    groupe_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """
    Delete a Groupe.
    
    ⚠️ Warning: This will cascade delete all related grand distributeurs and centres.
    """
    try:
        GroupeService.delete(db, groupe_id)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{groupe_id}/activate", response_model=GroupeRead)
def activate_groupe(
    groupe_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Activate a Groupe."""
    try:
        groupe = GroupeService.activate(db, groupe_id)
        return groupe
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{groupe_id}/deactivate", response_model=GroupeRead)
def deactivate_groupe(
    groupe_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Deactivate a Groupe."""
    try:
        groupe = GroupeService.deactivate(db, groupe_id)
        return groupe
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

