"""
Bon d'Enlèvement Service

Business logic for BonEnlevement workflow operations.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.bon_enlevement import BonEnlevement, BonEnlevementStatus
from app.models.centre_remplisseur import CentreRemplisseur
from app.models.partner import Partner
from app.models.depot import Depot
from app.models.palette import Palette, PaletteStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.user import User
from app.schemas.bon_enlevement import (
    BonEnlevementCreate,
    BonEnlevementUpdate,
    BonEnlevementValidation,
    BonEnlevementChargement,
    BonEnlevementDepart,
    BonEnlevementReception,
    BonEnlevementStatusUpdate
)
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    BusinessRuleException
)


class BonEnlevementService:
    """Service for BonEnlevement workflow operations."""
    
    @staticmethod
    def _generate_numero_bon() -> str:
        """
        Generate a unique Bon d'Enlèvement number.
        
        Format: XXXXXXXX/MM (8 digits + month)
        Example: 00000201/08
        
        Returns:
            Generated numero
        """
        current_month = datetime.now().strftime("%m")
        # In production, get last number from DB and increment
        # For now, generate random 8-digit number
        number = secrets.randbelow(100000000)
        return f"{number:08d}/{current_month}"
    
    @staticmethod
    def _generate_otp() -> tuple[str, datetime]:
        """
        Generate OTP code for delivery validation.
        
        Returns:
            Tuple of (otp_code, expiry_datetime)
        """
        otp = str(secrets.randbelow(1000000)).zfill(6)
        expiry = datetime.utcnow() + timedelta(hours=24)
        return otp, expiry
    
    @staticmethod
    def create(db: Session, schema: BonEnlevementCreate, created_by_id: UUID) -> BonEnlevement:
        """
        Create a new Bon d'Enlèvement.
        
        Args:
            db: Database session
            schema: BonEnlevement creation schema
            created_by_id: ID of user creating the bon
            
        Returns:
            Created BonEnlevement
            
        Raises:
            NotFoundException: If Centre, Grossiste, or Depot not found
            ValidationException: If validation fails
        """
        # Validate Centre Remplisseur exists
        centre = db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.id == schema.centre_remplisseur_id)
        ).scalar_one_or_none()
        
        if not centre or not centre.is_active:
            raise NotFoundException(f"Centre Remplisseur with ID {schema.centre_remplisseur_id} not found or inactive")
        
        # Validate Grossiste exists
        grossiste = db.execute(
            select(Partner).where(Partner.id == schema.grossiste_id)
        ).scalar_one_or_none()
        
        if not grossiste:
            raise NotFoundException(f"Grossiste with ID {schema.grossiste_id} not found")
        
        # Validate Depot Principal if provided
        if schema.depot_principal_id:
            depot = db.execute(
                select(Depot).where(Depot.id == schema.depot_principal_id)
            ).scalar_one_or_none()
            
            if not depot or depot.partner_id != schema.grossiste_id:
                raise ValidationException(f"Depot {schema.depot_principal_id} not found or doesn't belong to grossiste")
        
        # Generate unique numero_bon
        numero_bon = BonEnlevementService._generate_numero_bon()
        
        # Create Bon d'Enlèvement
        bon_data = schema.model_dump()
        bon_data['numero_bon'] = numero_bon
        bon_data['status'] = BonEnlevementStatus.CREATION
        bon_data['date_creation'] = datetime.utcnow()
        
        bon = BonEnlevement(**bon_data)
        db.add(bon)
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def get_by_id(db: Session, bon_id: UUID) -> BonEnlevement:
        """
        Get BonEnlevement by ID.
        
        Args:
            db: Database session
            bon_id: BonEnlevement ID
            
        Returns:
            BonEnlevement
            
        Raises:
            NotFoundException: If not found
        """
        bon = db.execute(
            select(BonEnlevement).where(BonEnlevement.id == bon_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon d'Enlèvement with ID {bon_id} not found")
        
        return bon
    
    @staticmethod
    def get_by_numero(db: Session, numero_bon: str) -> Optional[BonEnlevement]:
        """Get BonEnlevement by numero_bon."""
        return db.execute(
            select(BonEnlevement).where(BonEnlevement.numero_bon == numero_bon)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        centre_id: Optional[UUID] = None,
        grossiste_id: Optional[UUID] = None,
        status: Optional[BonEnlevementStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> List[BonEnlevement]:
        """Get all BonEnlevements with filtering."""
        query = select(BonEnlevement)
        
        if centre_id:
            query = query.where(BonEnlevement.centre_remplisseur_id == centre_id)
        
        if grossiste_id:
            query = query.where(BonEnlevement.grossiste_id == grossiste_id)
        
        if status:
            query = query.where(BonEnlevement.status == status)
        
        if date_from:
            query = query.where(BonEnlevement.date_creation >= date_from)
        
        if date_to:
            query = query.where(BonEnlevement.date_creation <= date_to)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (BonEnlevement.numero_bon.ilike(search_pattern)) |
                (BonEnlevement.chauffeur_nom.ilike(search_pattern)) |
                (BonEnlevement.vehicule_immatriculation.ilike(search_pattern))
            )
        
        query = query.order_by(BonEnlevement.date_creation.desc()).offset(skip).limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def update(db: Session, bon_id: UUID, schema: BonEnlevementUpdate) -> BonEnlevement:
        """
        Update BonEnlevement (only editable fields).
        
        Can only update if status is CREATION.
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.CREATION:
            raise BusinessRuleException("Can only update Bon d'Enlèvement in CREATION status")
        
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bon, field, value)
        
        db.commit()
        db.refresh(bon)
        return bon
    
    @staticmethod
    def valider(db: Session, bon_id: UUID, validation: BonEnlevementValidation) -> BonEnlevement:
        """
        Validate a Bon d'Enlèvement (Centre Remplisseur validates the order).
        
        Status: CREATION -> VALIDE
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.CREATION:
            raise BusinessRuleException(f"Can only validate Bon in CREATION status, current: {bon.status}")
        
        # Verify validateur exists
        validateur = db.execute(
            select(User).where(User.id == validation.validateur_centre_id)
        ).scalar_one_or_none()
        
        if not validateur:
            raise NotFoundException(f"Validateur with ID {validation.validateur_centre_id} not found")
        
        # Generate OTP for final delivery validation
        otp, otp_expiry = BonEnlevementService._generate_otp()
        
        # Update Bon
        bon.status = BonEnlevementStatus.VALIDE
        bon.date_validation = datetime.utcnow()
        bon.validateur_centre_id = validation.validateur_centre_id
        bon.otp_code = otp
        bon.otp_expiry = otp_expiry
        
        if validation.observations:
            bon.observations = validation.observations
        
        db.commit()
        db.refresh(bon)
        
        # TODO: Send OTP to grossiste via SMS/Email
        
        return bon
    
    @staticmethod
    def start_chargement(
        db: Session,
        bon_id: UUID,
        chargement: BonEnlevementChargement,
        user_id: UUID
    ) -> BonEnlevement:
        """
        Start loading palettes onto the truck.
        
        Status: VALIDE -> EN_CHARGEMENT
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.VALIDE:
            raise BusinessRuleException(f"Can only start loading from VALIDE status, current: {bon.status}")
        
        # Validate all palettes exist and are available
        for palette_id in chargement.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            if not palette:
                raise NotFoundException(f"Palette {palette_id} not found")
            
            if not palette.can_be_assigned_for_delivery():
                raise BusinessRuleException(
                    f"Palette {palette_id} not available for delivery (status: {palette.status}, full: {palette.is_full})"
                )
        
        # Update Bon status
        bon.status = BonEnlevementStatus.EN_CHARGEMENT
        bon.date_chargement = datetime.utcnow()
        
        if chargement.observations:
            bon.observations = chargement.observations
        
        # Assign palettes to bon and update their status
        for palette_id in chargement.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            palette.status = PaletteStatus.EN_CHARGEMENT
            palette.bon_enlevement_actuel_id = bon.id
            
            # Create movement record
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_enlevement_id=bon.id,
                centre_remplisseur_id=bon.centre_remplisseur_id,
                user_id=user_id,
                action=MovementAction.CHARGEMENT_CENTRE,
                status_before=PaletteStatus.AU_CENTRE.value,
                status_after=PaletteStatus.EN_CHARGEMENT.value,
                notes=f"Chargement pour Bon d'Enlèvement {bon.numero_bon}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def depart(db: Session, bon_id: UUID, depart: BonEnlevementDepart, user_id: UUID) -> BonEnlevement:
        """
        Mark departure from Centre Remplisseur.
        
        Status: EN_CHARGEMENT -> EN_ROUTE
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.EN_CHARGEMENT:
            raise BusinessRuleException(f"Can only depart from EN_CHARGEMENT status, current: {bon.status}")
        
        # Check that palettes are loaded
        palettes_count = db.execute(
            select(func.count(Palette.id)).where(Palette.bon_enlevement_actuel_id == bon.id)
        ).scalar()
        
        if palettes_count == 0:
            raise BusinessRuleException("Cannot depart without loaded palettes")
        
        # Update Bon
        bon.status = BonEnlevementStatus.EN_ROUTE
        bon.date_depart = depart.date_depart or datetime.utcnow()
        
        if depart.observations:
            bon.observations = depart.observations
        
        # Update all palettes to EN_ROUTE_LIVRAISON
        palettes = db.execute(
            select(Palette).where(Palette.bon_enlevement_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.EN_ROUTE_LIVRAISON
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_enlevement_id=bon.id,
                centre_remplisseur_id=bon.centre_remplisseur_id,
                user_id=user_id,
                action=MovementAction.DEPART_CENTRE,
                status_before=old_status.value,
                status_after=PaletteStatus.EN_ROUTE_LIVRAISON.value,
                timestamp=bon.date_depart,
                notes=f"Départ du centre pour Bon {bon.numero_bon}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def start_livraison(db: Session, bon_id: UUID) -> BonEnlevement:
        """
        Mark start of multi-depot deliveries.
        
        Status: EN_ROUTE -> EN_LIVRAISON
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.EN_ROUTE:
            raise BusinessRuleException(f"Can only start livraison from EN_ROUTE status, current: {bon.status}")
        
        bon.status = BonEnlevementStatus.EN_LIVRAISON
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def terminer(
        db: Session,
        bon_id: UUID,
        reception: BonEnlevementReception,
        user_id: UUID
    ) -> BonEnlevement:
        """
        Complete the Bon d'Enlèvement (final reception at main depot).
        
        Status: EN_LIVRAISON -> TERMINE
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status != BonEnlevementStatus.EN_LIVRAISON:
            raise BusinessRuleException(f"Can only terminate from EN_LIVRAISON status, current: {bon.status}")
        
        # Validate OTP if provided
        if reception.otp_code:
            if bon.otp_code != reception.otp_code:
                raise ValidationException("Invalid OTP code")
            
            if bon.otp_expiry and datetime.utcnow() > bon.otp_expiry:
                raise ValidationException("OTP code expired")
        
        # Verify recepteur exists
        recepteur = db.execute(
            select(User).where(User.id == reception.recepteur_final_id)
        ).scalar_one_or_none()
        
        if not recepteur:
            raise NotFoundException(f"Recepteur with ID {reception.recepteur_final_id} not found")
        
        # Update Bon
        bon.status = BonEnlevementStatus.TERMINE
        bon.date_arrivee_finale = reception.date_arrivee_finale or datetime.utcnow()
        bon.recepteur_final_id = reception.recepteur_final_id
        
        if reception.observations:
            bon.observations = reception.observations
        
        # Update remaining palettes (those that went to main depot)
        palettes = db.execute(
            select(Palette).where(Palette.bon_enlevement_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.AU_DEPOT
            palette.bon_enlevement_actuel_id = None
            palette.current_depot_id = bon.depot_principal_id
            palette.current_centre_remplisseur_id = None
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_enlevement_id=bon.id,
                depot_id=bon.depot_principal_id,
                user_id=user_id,
                action=MovementAction.ARRIVEE_DEPOT,
                status_before=old_status.value,
                status_after=PaletteStatus.AU_DEPOT.value,
                timestamp=bon.date_arrivee_finale,
                notes=f"Arrivée finale - Bon {bon.numero_bon}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def annuler(db: Session, bon_id: UUID, reason: str, user_id: UUID) -> BonEnlevement:
        """
        Cancel a Bon d'Enlèvement.
        
        Can only cancel if status is CREATION or VALIDE.
        """
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        if bon.status not in [BonEnlevementStatus.CREATION, BonEnlevementStatus.VALIDE]:
            raise BusinessRuleException(f"Cannot cancel Bon in status {bon.status}")
        
        # If palettes were assigned, unassign them
        if bon.status == BonEnlevementStatus.VALIDE:
            palettes = db.execute(
                select(Palette).where(Palette.bon_enlevement_actuel_id == bon.id)
            ).scalars().all()
            
            for palette in palettes:
                palette.bon_enlevement_actuel_id = None
                palette.status = PaletteStatus.AU_CENTRE
        
        bon.status = BonEnlevementStatus.ANNULE
        bon.observations = f"ANNULÉ: {reason}"
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def get_with_stats(db: Session, bon_id: UUID) -> dict:
        """Get BonEnlevement with statistics."""
        bon = BonEnlevementService.get_by_id(db, bon_id)
        
        # Count palettes
        palettes_count = db.execute(
            select(func.count(Palette.id)).where(
                (Palette.bon_enlevement_actuel_id == bon.id) |
                (Palette.id.in_(
                    select(PaletteMovement.palette_id).where(
                        PaletteMovement.bon_enlevement_id == bon.id
                    )
                ))
            )
        ).scalar() or 0
        
        # Count livraisons
        livraisons_count = db.execute(
            select(func.count()).select_from(BonEnlevement).join(
                BonEnlevement.livraisons
            ).where(BonEnlevement.id == bon.id)
        ).scalar() or 0
        
        # Count collectes
        collectes_count = db.execute(
            select(func.count()).select_from(BonEnlevement).join(
                BonEnlevement.collectes_vides
            ).where(BonEnlevement.id == bon.id)
        ).scalar() or 0
        
        return {
            "bon": bon,
            "centre_name": bon.centre_remplisseur.name if bon.centre_remplisseur else None,
            "grossiste_name": bon.grossiste.name if bon.grossiste else None,
            "depot_principal_name": bon.depot_principal.name if bon.depot_principal else None,
            "palettes_count": palettes_count,
            "livraisons_count": livraisons_count,
            "collectes_count": collectes_count,
        }

