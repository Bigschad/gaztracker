"""
Expedition Routes

API endpoints for expedition management including CRUD operations,
palette assignment, departure tracking, and OTP validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import math

from app.database import get_sync_db
from app.models.user import User
from app.models.expedition import ExpeditionStatus
from app.schemas.expedition import (
    ExpeditionCreate,
    ExpeditionUpdate,
    ExpeditionResponse,
    ExpeditionListResponse,
    ExpeditionDepartRequest,
    ExpeditionValidateRequest,
    ExpeditionStatistics
)
from app.services.expedition_service import ExpeditionService
from app.middleware.auth_middleware import get_current_user_sync
from app.middleware.rbac import require_role
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    PaletteNotAvailableException,
    InvalidStatusTransitionException,
    InvalidOTPException
)

router = APIRouter()


@router.post(
    "",
    response_model=ExpeditionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expedition",
    description="Create a new expedition and optionally assign palettes to it."
)
async def create_expedition(
    expedition_create: ExpeditionCreate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE", "OPERATEUR_USINE"]))
):
    """
    Create a new expedition.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE, OPERATEUR_USINE

    The expedition will be created with status CREATION.
    Palettes can be assigned during creation or later.
    """
    try:
        expedition = ExpeditionService.create_expedition(
            db=db,
            expedition_create=expedition_create,
            current_user=current_user
        )
        return expedition
    except (ValidationException, PaletteNotAvailableException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=ExpeditionListResponse,
    summary="List expeditions",
    description="Get a paginated list of expeditions with optional filters."
)
async def list_expeditions(
    status_filter: Optional[ExpeditionStatus] = Query(None, alias="status", description="Filter by status"),
    created_by_id: Optional[UUID] = Query(None, description="Filter by creator user ID"),
    search: Optional[str] = Query(None, description="Search in reference, transporter, or destination"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    List all expeditions with pagination and filters.

    Supports filtering by:
    - Status
    - Creator user ID
    - Search term (in reference number, transporter, or destination)
    """
    expeditions, total = ExpeditionService.list_expeditions(
        db=db,
        status=status_filter,
        created_by_id=created_by_id,
        search=search,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ExpeditionListResponse(
        items=expeditions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{expedition_id}",
    response_model=ExpeditionResponse,
    summary="Get expedition details",
    description="Get detailed information about a specific expedition."
)
async def get_expedition(
    expedition_id: UUID,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Get details of a specific expedition by ID.
    """
    try:
        expedition = ExpeditionService.get_expedition(
            db=db,
            expedition_id=expedition_id
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{expedition_id}",
    response_model=ExpeditionResponse,
    summary="Update expedition",
    description="Update expedition details. Some fields can only be updated in certain statuses."
)
async def update_expedition(
    expedition_id: UUID,
    expedition_update: ExpeditionUpdate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE", "OPERATEUR_USINE"]))
):
    """
    Update an expedition.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE, OPERATEUR_USINE

    Note: Expeditions can only be fully modified in CREATION or EN_ATTENTE status.
    Status transitions must follow the defined workflow.
    """
    try:
        expedition = ExpeditionService.update_expedition(
            db=db,
            expedition_id=expedition_id,
            expedition_update=expedition_update,
            current_user=current_user
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ValidationException, InvalidStatusTransitionException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{expedition_id}/palettes",
    response_model=ExpeditionResponse,
    summary="Assign palettes to expedition",
    description="Assign one or more palettes to an expedition."
)
async def assign_palettes(
    expedition_id: UUID,
    palette_ids: List[UUID],
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE", "OPERATEUR_USINE"]))
):
    """
    Assign palettes to an expedition.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE, OPERATEUR_USINE

    Palettes can only be assigned to expeditions in CREATION, EN_ATTENTE, or CREEE status.
    """
    try:
        expedition = ExpeditionService.assign_palettes(
            db=db,
            expedition_id=expedition_id,
            palette_ids=palette_ids,
            current_user=current_user
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ValidationException, PaletteNotAvailableException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{expedition_id}/depart",
    response_model=ExpeditionResponse,
    summary="Mark expedition as departed",
    description="Mark an expedition as departed and generate an OTP for delivery validation."
)
async def mark_as_departed(
    expedition_id: UUID,
    depart_request: ExpeditionDepartRequest,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE", "CHAUFFEUR"]))
):
    """
    Mark an expedition as departed.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE, CHAUFFEUR

    This endpoint:
    1. Changes expedition status to EN_TRANSIT
    2. Sets the departure date
    3. Generates an OTP for delivery validation
    4. Updates all assigned palettes to EN_ROUTE status

    The expedition must be in CREEE or EN_ATTENTE status and must have at least one palette assigned.
    """
    try:
        expedition = ExpeditionService.mark_as_departed(
            db=db,
            expedition_id=expedition_id,
            depart_request=depart_request,
            current_user=current_user
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{expedition_id}/validate",
    response_model=ExpeditionResponse,
    summary="Validate expedition delivery",
    description="Validate expedition delivery using OTP code."
)
async def validate_delivery(
    expedition_id: UUID,
    validate_request: ExpeditionValidateRequest,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Validate expedition delivery with OTP.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This endpoint:
    1. Validates the provided OTP code
    2. Changes expedition status to LIVREE
    3. Sets the delivery date
    4. Updates all assigned palettes to LIVREE status

    The expedition must be in EN_TRANSIT or ARRIVEE status.
    The OTP must match and not be expired.
    """
    try:
        expedition = ExpeditionService.validate_delivery(
            db=db,
            expedition_id=expedition_id,
            validate_request=validate_request,
            current_user=current_user
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidOTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{expedition_id}",
    response_model=ExpeditionResponse,
    summary="Cancel expedition",
    description="Cancel an expedition and release all assigned palettes."
)
async def cancel_expedition(
    expedition_id: UUID,
    reason: str = Query(..., description="Reason for cancellation"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Cancel an expedition.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This endpoint:
    1. Changes expedition status to ANNULEE
    2. Releases all assigned palettes back to EN_STOCK
    3. Records the cancellation reason

    Completed expeditions (LIVREE) cannot be cancelled.
    """
    try:
        expedition = ExpeditionService.cancel_expedition(
            db=db,
            expedition_id=expedition_id,
            reason=reason,
            current_user=current_user
        )
        return expedition
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/statistics/overview",
    response_model=ExpeditionStatistics,
    summary="Get expedition statistics",
    description="Get statistical overview of all expeditions."
)
async def get_statistics(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get expedition statistics.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns:
    - Total number of expeditions
    - Count by status
    - Number of expeditions in transit
    - Number of delivered expeditions
    - Number of delayed expeditions
    """
    stats = ExpeditionService.get_expedition_statistics(db=db)
    return ExpeditionStatistics(**stats)
