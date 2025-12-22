"""
Bons d'Enlèvement API Routes

Workflow endpoints for Bon d'Enlèvement (outbound delivery management).
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.models.bon_enlevement import BonEnlevementStatus
from app.models.user import User
from app.middleware.auth_middleware import get_current_user_sync
from app.services.bon_enlevement_service import BonEnlevementService
from app.schemas.bon_enlevement import (
    BonEnlevementCreate,
    BonEnlevementUpdate,
    BonEnlevementRead,
    BonEnlevementList,
    BonEnlevementDetail,
    BonEnlevementValidation,
    BonEnlevementChargement,
    BonEnlevementDepart,
    BonEnlevementReception
)
from app.core.exceptions import NotFoundException, BusinessRuleException, ValidationException


router = APIRouter()


@router.post("/", response_model=BonEnlevementRead, status_code=status.HTTP_201_CREATED)
def create_bon(
    schema: BonEnlevementCreate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Create a new Bon d'Enlèvement.
    
    Initial status: CREATION
    
    - **centre_remplisseur_id**: Origin filling center
    - **grossiste_id**: Ordering grossiste
    - **depot_principal_id**: Final destination depot (optional)
    - **vehicule_immatriculation**, **chauffeur_nom**, **chauffeur_societe**: Transport details
    """
    try:
        bon = BonEnlevementService.create(db, schema, current_user.id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[BonEnlevementList])
def list_bons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    centre_id: Optional[UUID] = None,
    grossiste_id: Optional[UUID] = None,
    status_filter: Optional[BonEnlevementStatus] = Query(None, alias="status"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all Bons d'Enlèvement with filtering.
    
    - **centre_id**: Filter by centre remplisseur
    - **grossiste_id**: Filter by grossiste
    - **status**: Filter by status
    - **date_from**, **date_to**: Filter by creation date range
    - **search**: Search by numero_bon, chauffeur, or vehicle
    """
    bons = BonEnlevementService.get_all(
        db,
        skip=skip,
        limit=limit,
        centre_id=centre_id,
        grossiste_id=grossiste_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        search=search
    )
    return bons


@router.get("/{bon_id}", response_model=BonEnlevementDetail)
def get_bon(
    bon_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Get a Bon d'Enlèvement by ID with statistics."""
    try:
        stats = BonEnlevementService.get_with_stats(db, bon_id)
        
        bon = stats["bon"]
        return BonEnlevementDetail(
            **{
                "id": bon.id,
                "numero_bon": bon.numero_bon,
                "reference": bon.reference,
                "centre_remplisseur_id": bon.centre_remplisseur_id,
                "grossiste_id": bon.grossiste_id,
                "depot_principal_id": bon.depot_principal_id,
                "vehicule_immatriculation": bon.vehicule_immatriculation,
                "chauffeur_nom": bon.chauffeur_nom,
                "chauffeur_societe": bon.chauffeur_societe,
                "chauffeur_phone": bon.chauffeur_phone,
                "status": bon.status,
                "date_creation": bon.date_creation,
                "date_validation": bon.date_validation,
                "date_chargement": bon.date_chargement,
                "date_depart": bon.date_depart,
                "date_arrivee_finale": bon.date_arrivee_finale,
                "validateur_centre_id": bon.validateur_centre_id,
                "recepteur_final_id": bon.recepteur_final_id,
                "observations": bon.observations,
                "instructions_livraison": bon.instructions_livraison,
                "created_at": bon.created_at,
                "updated_at": bon.updated_at,
                "centre_remplisseur_name": stats["centre_name"],
                "grossiste_name": stats["grossiste_name"],
                "depot_principal_name": stats["depot_principal_name"],
                "palettes_count": stats["palettes_count"],
                "livraisons_count": stats["livraisons_count"],
                "collectes_count": stats["collectes_count"]
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{bon_id}", response_model=BonEnlevementRead)
def update_bon(
    bon_id: UUID,
    schema: BonEnlevementUpdate,
    db: Session = Depends(get_sync_db)
):
    """
    Update a Bon d'Enlèvement (only in CREATION status).
    
    Only editable fields can be updated.
    """
    try:
        bon = BonEnlevementService.update(db, bon_id, schema)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/valider", response_model=BonEnlevementRead)
def valider_bon(
    bon_id: UUID,
    validation: BonEnlevementValidation,
    db: Session = Depends(get_sync_db)
):
    """
    Validate a Bon d'Enlèvement (CREATION → VALIDE).
    
    - Centre validates the order
    - Generates OTP for final delivery validation
    - Transition: CREATION → VALIDE
    """
    try:
        bon = BonEnlevementService.valider(db, bon_id, validation)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/start-chargement", response_model=BonEnlevementRead)
def start_chargement(
    bon_id: UUID,
    chargement: BonEnlevementChargement,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Start loading palettes (VALIDE → EN_CHARGEMENT).
    
    - Assigns palettes to the bon
    - Updates palette statuses
    - Creates movement records
    - Transition: VALIDE → EN_CHARGEMENT
    """
    try:
        bon = BonEnlevementService.start_chargement(db, bon_id, chargement, current_user.id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/depart", response_model=BonEnlevementRead)
def depart(
    bon_id: UUID,
    depart: BonEnlevementDepart,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Mark departure from centre (EN_CHARGEMENT → EN_ROUTE).
    
    - Updates all palettes to EN_ROUTE_LIVRAISON
    - Records departure time
    - Transition: EN_CHARGEMENT → EN_ROUTE
    """
    try:
        bon = BonEnlevementService.depart(db, bon_id, depart, current_user.id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/start-livraison", response_model=BonEnlevementRead)
def start_livraison(
    bon_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """
    Start deliveries (EN_ROUTE → EN_LIVRAISON).
    
    Used when starting multi-depot delivery tour.
    Transition: EN_ROUTE → EN_LIVRAISON
    """
    try:
        bon = BonEnlevementService.start_livraison(db, bon_id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/terminer", response_model=BonEnlevementRead)
def terminer_bon(
    bon_id: UUID,
    reception: BonEnlevementReception,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Complete the Bon d'Enlèvement (EN_LIVRAISON → TERMINE).
    
    - Final reception at main depot
    - Validates OTP if provided
    - Updates remaining palettes to AU_DEPOT
    - Transition: EN_LIVRAISON → TERMINE
    """
    try:
        bon = BonEnlevementService.terminer(db, bon_id, reception, current_user.id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/annuler")
def annuler_bon(
    bon_id: UUID,
    reason: str = Query(..., min_length=5, max_length=500),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Cancel a Bon d'Enlèvement.
    
    Can only cancel if status is CREATION or VALIDE.
    Unassigns palettes if any were assigned.
    """
    try:
        bon = BonEnlevementService.annuler(db, bon_id, reason, current_user.id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

