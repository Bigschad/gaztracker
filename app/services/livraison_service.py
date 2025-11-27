"""
Livraison Detail Service

Business logic for LivraisonDetail operations (multi-depot delivery management).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.livraison_detail import LivraisonDetail, LivraisonStatus
from app.models.bon_enlevement import BonEnlevement, BonEnlevementStatus
from app.models.depot import Depot
from app.models.partner import Partner
from app.models.palette import Palette, PaletteStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.schemas.livraison_detail import (
    LivraisonDetailCreate,
    LivraisonDetailUpdate,
    LivraisonDetailArrivee,
    LivraisonDetailCompletion,
    LivraisonDetailProbleme
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException
)


class LivraisonService:
    """Service for LivraisonDetail operations."""
    
    @staticmethod
    def create(db: Session, schema: LivraisonDetailCreate) -> LivraisonDetail:
        """
        Create a new LivraisonDetail (delivery stop).
        
        Args:
            db: Database session
            schema: LivraisonDetail creation schema
            
        Returns:
            Created LivraisonDetail
            
        Raises:
            NotFoundException: If BonEnlevement or Depot not found
            ValidationException: If validation fails
        """
        # Validate BonEnlevement exists
        bon = db.execute(
            select(BonEnlevement).where(BonEnlevement.id == schema.bon_enlevement_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon d'Enlèvement {schema.bon_enlevement_id} not found")
        
        # Can only add livraisons to VALIDE or EN_CHARGEMENT bons
        if bon.status not in [BonEnlevementStatus.VALIDE, BonEnlevementStatus.EN_CHARGEMENT]:
            raise BusinessRuleException(f"Cannot add livraison to Bon in status {bon.status}")
        
        # Validate Depot exists
        depot = db.execute(
            select(Depot).where(Depot.id == schema.depot_id)
        ).scalar_one_or_none()
        
        if not depot or not depot.is_active:
            raise NotFoundException(f"Depot {schema.depot_id} not found or inactive")
        
        # Validate Revendeur if provided
        if schema.revendeur_id:
            revendeur = db.execute(
                select(Partner).where(Partner.id == schema.revendeur_id)
            ).scalar_one_or_none()
            
            if not revendeur:
                raise NotFoundException(f"Revendeur {schema.revendeur_id} not found")
            
            # Verify depot belongs to revendeur
            if depot.partner_id != schema.revendeur_id:
                raise ValidationException(f"Depot {depot.id} doesn't belong to revendeur {schema.revendeur_id}")
        
        # Create LivraisonDetail
        livraison = LivraisonDetail(**schema.model_dump())
        livraison.status = LivraisonStatus.EN_ATTENTE
        
        db.add(livraison)
        db.commit()
        db.refresh(livraison)
        
        return livraison
    
    @staticmethod
    def get_by_id(db: Session, livraison_id: UUID) -> LivraisonDetail:
        """Get LivraisonDetail by ID."""
        livraison = db.execute(
            select(LivraisonDetail).where(LivraisonDetail.id == livraison_id)
        ).scalar_one_or_none()
        
        if not livraison:
            raise NotFoundException(f"LivraisonDetail {livraison_id} not found")
        
        return livraison
    
    @staticmethod
    def get_all_for_bon(db: Session, bon_id: UUID) -> List[LivraisonDetail]:
        """Get all livraisons for a Bon d'Enlèvement, ordered by ordre_livraison."""
        result = db.execute(
            select(LivraisonDetail)
            .where(LivraisonDetail.bon_enlevement_id == bon_id)
            .order_by(LivraisonDetail.ordre_livraison)
        )
        return list(result.scalars().all())
    
    @staticmethod
    def update(db: Session, livraison_id: UUID, schema: LivraisonDetailUpdate) -> LivraisonDetail:
        """
        Update LivraisonDetail.
        
        Can only update if status is EN_ATTENTE.
        """
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        if livraison.status != LivraisonStatus.EN_ATTENTE:
            raise BusinessRuleException(f"Cannot update livraison in status {livraison.status}")
        
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(livraison, field, value)
        
        db.commit()
        db.refresh(livraison)
        
        return livraison
    
    @staticmethod
    def marquer_arrivee(
        db: Session,
        livraison_id: UUID,
        arrivee: LivraisonDetailArrivee
    ) -> LivraisonDetail:
        """
        Mark arrival at delivery point.
        
        Status: EN_ATTENTE -> EN_COURS
        """
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        if livraison.status != LivraisonStatus.EN_ATTENTE:
            raise BusinessRuleException(f"Can only mark arrival from EN_ATTENTE status, current: {livraison.status}")
        
        # Update status
        livraison.status = LivraisonStatus.EN_COURS
        livraison.date_arrivee = arrivee.date_arrivee or datetime.utcnow()
        livraison.latitude_arrivee = arrivee.latitude_arrivee
        livraison.longitude_arrivee = arrivee.longitude_arrivee
        
        if arrivee.observations:
            livraison.observations = arrivee.observations
        
        # Update Bon status to EN_LIVRAISON if not already
        bon = livraison.bon_enlevement
        if bon.status == BonEnlevementStatus.EN_ROUTE:
            bon.status = BonEnlevementStatus.EN_LIVRAISON
        
        db.commit()
        db.refresh(livraison)
        
        return livraison
    
    @staticmethod
    def completer_livraison(
        db: Session,
        livraison_id: UUID,
        completion: LivraisonDetailCompletion,
        user_id: UUID
    ) -> LivraisonDetail:
        """
        Complete a delivery (with signature and palette unloading).
        
        Status: EN_COURS -> LIVREE
        """
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        if livraison.status != LivraisonStatus.EN_COURS:
            raise BusinessRuleException(f"Can only complete from EN_COURS status, current: {livraison.status}")
        
        # Validate all palettes exist and belong to the bon
        for palette_id in completion.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            if not palette:
                raise NotFoundException(f"Palette {palette_id} not found")
            
            if palette.bon_enlevement_actuel_id != livraison.bon_enlevement_id:
                raise ValidationException(f"Palette {palette_id} doesn't belong to this bon d'enlèvement")
        
        # Update livraison
        livraison.status = LivraisonStatus.LIVREE
        livraison.date_depart = completion.date_depart or datetime.utcnow()
        livraison.recepteur_nom = completion.recepteur_nom
        livraison.recepteur_signature = completion.recepteur_signature
        
        if completion.observations:
            livraison.observations = completion.observations
        
        # Update palettes: unload them at this depot
        for palette_id in completion.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            old_status = palette.status
            palette.status = PaletteStatus.AU_DEPOT
            palette.bon_enlevement_actuel_id = None  # No longer on the truck
            palette.current_depot_id = livraison.depot_id
            palette.current_centre_remplisseur_id = None
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_enlevement_id=livraison.bon_enlevement_id,
                livraison_detail_id=livraison.id,
                depot_id=livraison.depot_id,
                user_id=user_id,
                action=MovementAction.LIVRAISON_DEPOT,
                status_before=old_status.value,
                status_after=PaletteStatus.AU_DEPOT.value,
                timestamp=livraison.date_depart,
                notes=f"Livraison à {livraison.depot.name if livraison.depot else 'depot'}"
            )
            db.add(movement)
            
            # Associate palette with livraison (many-to-many)
            livraison.palettes_livrees.append(palette)
        
        db.commit()
        db.refresh(livraison)
        
        return livraison
    
    @staticmethod
    def signaler_probleme(
        db: Session,
        livraison_id: UUID,
        probleme: LivraisonDetailProbleme
    ) -> LivraisonDetail:
        """
        Report a problem with delivery.
        
        Status: EN_COURS -> PROBLEME
        """
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        if livraison.status != LivraisonStatus.EN_COURS:
            raise BusinessRuleException(f"Can only report problem from EN_COURS status, current: {livraison.status}")
        
        livraison.status = LivraisonStatus.PROBLEME
        livraison.problemes = probleme.problemes
        
        if probleme.observations:
            livraison.observations = probleme.observations
        
        db.commit()
        db.refresh(livraison)
        
        # TODO: Send alert to centre and grossiste
        
        return livraison
    
    @staticmethod
    def annuler(db: Session, livraison_id: UUID, reason: str) -> LivraisonDetail:
        """
        Cancel a livraison.
        
        Can only cancel if status is EN_ATTENTE.
        """
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        if livraison.status != LivraisonStatus.EN_ATTENTE:
            raise BusinessRuleException(f"Can only cancel livraison in EN_ATTENTE status, current: {livraison.status}")
        
        livraison.status = LivraisonStatus.ANNULEE
        livraison.observations = f"ANNULÉE: {reason}"
        
        db.commit()
        db.refresh(livraison)
        
        return livraison
    
    @staticmethod
    def get_next_pending(db: Session, bon_id: UUID) -> Optional[LivraisonDetail]:
        """Get the next pending livraison for a bon (for guided tour)."""
        result = db.execute(
            select(LivraisonDetail)
            .where(
                (LivraisonDetail.bon_enlevement_id == bon_id) &
                (LivraisonDetail.status == LivraisonStatus.EN_ATTENTE)
            )
            .order_by(LivraisonDetail.ordre_livraison)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def get_with_stats(db: Session, livraison_id: UUID) -> dict:
        """Get LivraisonDetail with statistics."""
        livraison = LivraisonService.get_by_id(db, livraison_id)
        
        # Count palettes delivered
        palettes_count = db.execute(
            select(func.count()).select_from(LivraisonDetail).join(
                LivraisonDetail.palettes_livrees
            ).where(LivraisonDetail.id == livraison_id)
        ).scalar() or 0
        
        # Count collectes at this depot
        collectes_count = db.execute(
            select(func.count()).select_from(LivraisonDetail).join(
                LivraisonDetail.collectes_vides
            ).where(LivraisonDetail.id == livraison_id)
        ).scalar() or 0
        
        return {
            "livraison": livraison,
            "depot_name": livraison.depot.name if livraison.depot else None,
            "revendeur_name": livraison.revendeur.name if livraison.revendeur else None,
            "palettes_count": palettes_count,
            "collectes_count": collectes_count,
        }

