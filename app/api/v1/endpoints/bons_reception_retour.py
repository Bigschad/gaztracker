"""
Bons de Réception Retour API Routes

Workflow endpoints for Bon de Réception Retour (inbound return management).
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.models.bon_reception_retour import BonReceptionRetourStatus
from app.services.bon_reception_retour_service import BonReceptionRetourService
from app.schemas.bon_reception_retour import (
    BonReceptionRetourCreate,
    BonReceptionRetourUpdate,
    BonReceptionRetourRead,
    BonReceptionRetourList,
    BonReceptionRetourDetail,
    BonReceptionRetourDepart,
    BonReceptionRetourArrivee,
    BonReceptionRetourControle,
    BonReceptionRetourValidation,
    BonReceptionRetourRefus
)
from app.core.exceptions import NotFoundException, BusinessRuleException, ValidationException, DuplicateException


router = APIRouter()


@router.post("/", response_model=BonReceptionRetourRead, status_code=status.HTTP_201_CREATED)
def create_bon(
    schema: BonReceptionRetourCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new Bon de Réception Retour.
    
    Initial status: CREATION
    
    - **numero_bl**: BL number (e.g., "BL N°75 du 13.08.25")
    - **numero_reception**: Reception number (e.g., "0001320/08 MB")
    - **grossiste_id**: Grossiste returning palettes
    - **depot_depart_id**: Departure depot
    - **centre_remplisseur_id**: Destination filling center
    - **vehicule_immatriculation**, **transporteur_nom**: Transport details
    """
    try:
        # TODO: Get created_by_id from authenticated user
        created_by_id = UUID("00000000-0000-0000-0000-000000000001")  # Placeholder
        
        bon = BonReceptionRetourService.create(db, schema, created_by_id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[BonReceptionRetourList])
def list_bons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    grossiste_id: Optional[UUID] = None,
    centre_id: Optional[UUID] = None,
    status_filter: Optional[BonReceptionRetourStatus] = Query(None, alias="status"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all Bons de Réception Retour with filtering.
    
    - **grossiste_id**: Filter by grossiste
    - **centre_id**: Filter by centre remplisseur
    - **status**: Filter by status
    - **date_from**, **date_to**: Filter by creation date range
    - **search**: Search by numero_bl, numero_reception, transporteur, or vehicle
    """
    bons = BonReceptionRetourService.get_all(
        db,
        skip=skip,
        limit=limit,
        grossiste_id=grossiste_id,
        centre_id=centre_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        search=search
    )
    return bons


@router.get("/{bon_id}", response_model=BonReceptionRetourDetail)
def get_bon(
    bon_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Get a Bon de Réception Retour by ID with statistics."""
    try:
        stats = BonReceptionRetourService.get_with_stats(db, bon_id)
        
        bon = stats["bon"]
        
        return BonReceptionRetourDetail(
            **{
                "id": bon.id,
                "numero_bl": bon.numero_bl,
                "numero_reception": bon.numero_reception,
                "grossiste_id": bon.grossiste_id,
                "depot_depart_id": bon.depot_depart_id,
                "centre_remplisseur_id": bon.centre_remplisseur_id,
                "vehicule_immatriculation": bon.vehicule_immatriculation,
                "transporteur_nom": bon.transporteur_nom,
                "transporteur_societe": bon.transporteur_societe,
                "status": bon.status,
                "date_creation": bon.date_creation,
                "date_depart": bon.date_depart,
                "date_arrivee": bon.date_arrivee,
                "date_controle": bon.date_controle,
                "date_validation": bon.date_validation,
                "controleur_id": bon.controleur_id,
                "magasinier_id": bon.magasinier_id,
                "observations": bon.observations,
                "manquants": bon.manquants,
                "client_signature": bon.client_signature,
                "magasinier_signature": bon.magasinier_signature,
                "controleur_signature": bon.controleur_signature,
                "palette_count": bon.palette_count,
                "palette_acceptees": bon.palette_acceptees,
                "palette_refusees": bon.palette_refusees,
                "created_at": bon.created_at,
                "updated_at": bon.updated_at,
                "grossiste_name": stats.get("grossiste_name"),
                "depot_depart_name": stats.get("depot_depart_name"),
                "centre_remplisseur_name": stats.get("centre_name"),
                "controleur_name": stats.get("controleur_name"),
                "magasinier_name": stats.get("magasinier_name"),
                "details_count": stats.get("details_count", 0),
                "taux_acceptation": stats.get("taux_acceptation")
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{bon_id}", response_model=BonReceptionRetourRead)
def update_bon(
    bon_id: UUID,
    schema: BonReceptionRetourUpdate,
    db: Session = Depends(get_sync_db)
):
    """
    Update a Bon de Réception Retour (only in CREATION status).
    
    Only editable fields can be updated.
    """
    try:
        bon = BonReceptionRetourService.update(db, bon_id, schema)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/depart", response_model=BonReceptionRetourRead)
def depart(
    bon_id: UUID,
    depart: BonReceptionRetourDepart,
    db: Session = Depends(get_sync_db)
):
    """
    Mark departure from depot with palettes (CREATION → EN_ROUTE).
    
    - Assigns palettes to the bon
    - Updates palette statuses to EN_ROUTE_RETOUR
    - Creates movement records
    - Transition: CREATION → EN_ROUTE
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = UUID("00000000-0000-0000-0000-000000000001")
        
        bon = BonReceptionRetourService.depart(db, bon_id, depart, user_id)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/arrivee", response_model=BonReceptionRetourRead)
def marquer_arrivee(
    bon_id: UUID,
    arrivee: BonReceptionRetourArrivee,
    db: Session = Depends(get_sync_db)
):
    """
    Mark arrival at Centre Remplisseur (EN_ROUTE → ARRIVE).
    
    - Records arrival time
    - Updates palette statuses to ARRIVE_CENTRE
    - Records warehouse keeper signature
    - Transition: EN_ROUTE → ARRIVE
    """
    try:
        bon = BonReceptionRetourService.marquer_arrivee(db, bon_id, arrivee)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/controle", response_model=BonReceptionRetourRead)
def controle_qualite(
    bon_id: UUID,
    controle: BonReceptionRetourControle,
    db: Session = Depends(get_sync_db)
):
    """
    Perform quality control on returned items (ARRIVE → EN_CONTROLE).
    
    - Creates DetailRetour records for each item type
    - Records quantities (prevue, recue, acceptee, refusee)
    - Records quality state (BON, MOYEN, MAUVAIS, REFUSE)
    - Records controller signature
    - Transition: ARRIVE → EN_CONTROLE
    """
    try:
        bon = BonReceptionRetourService.controle_qualite(db, bon_id, controle)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/valider", response_model=BonReceptionRetourRead)
def valider(
    bon_id: UUID,
    validation: BonReceptionRetourValidation,
    db: Session = Depends(get_sync_db)
):
    """
    Validate return reception (EN_CONTROLE → VALIDE).
    
    - All items accepted
    - Updates palettes to AU_CENTRE and is_full=False
    - Records client signature
    - Transition: EN_CONTROLE → VALIDE
    """
    try:
        bon = BonReceptionRetourService.valider(db, bon_id, validation)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{bon_id}/refuser", response_model=BonReceptionRetourRead)
def refuser(
    bon_id: UUID,
    refus: BonReceptionRetourRefus,
    db: Session = Depends(get_sync_db)
):
    """
    Refuse return reception (EN_CONTROLE → REFUSE).
    
    - Items rejected
    - Returns palettes to depot
    - Records refusal reason
    - Transition: EN_CONTROLE → REFUSE
    """
    try:
        bon = BonReceptionRetourService.refuser(db, bon_id, refus)
        return bon
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

