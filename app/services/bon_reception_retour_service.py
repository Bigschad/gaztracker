"""
Bon de Réception Retour Service

Business logic for BonReceptionRetour workflow operations (return journey).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from app.models.bon_reception_retour import BonReceptionRetour, BonReceptionRetourStatus
from app.models.detail_retour import DetailRetour, DetailRetourType, DetailRetourEtat
from app.models.partner import Partner
from app.models.depot import Depot
from app.models.centre_remplisseur import CentreRemplisseur
from app.models.palette import Palette, PaletteStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.user import User
from app.schemas.bon_reception_retour import (
    BonReceptionRetourCreate,
    BonReceptionRetourUpdate,
    BonReceptionRetourDepart,
    BonReceptionRetourArrivee,
    BonReceptionRetourControle,
    BonReceptionRetourValidation,
    BonReceptionRetourRefus
)
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    BusinessRuleException
)


class BonReceptionRetourService:
    """Service for BonReceptionRetour workflow operations."""
    
    @staticmethod
    def create(db: Session, schema: BonReceptionRetourCreate, created_by_id: UUID) -> BonReceptionRetour:
        """
        Create a new Bon de Réception Retour.
        
        Args:
            db: Database session
            schema: BonReceptionRetour creation schema
            created_by_id: ID of user creating the bon
            
        Returns:
            Created BonReceptionRetour
            
        Raises:
            NotFoundException: If Grossiste, Depot, or Centre not found
            DuplicateException: If numero_bl or numero_reception already exists
        """
        # Validate Grossiste exists
        grossiste = db.execute(
            select(Partner).where(Partner.id == schema.grossiste_id)
        ).scalar_one_or_none()
        
        if not grossiste:
            raise NotFoundException(f"Grossiste with ID {schema.grossiste_id} not found")
        
        # Validate Depot exists and belongs to Grossiste
        depot = db.execute(
            select(Depot).where(Depot.id == schema.depot_depart_id)
        ).scalar_one_or_none()
        
        if not depot or depot.partner_id != schema.grossiste_id:
            raise ValidationException(f"Depot {schema.depot_depart_id} not found or doesn't belong to grossiste")
        
        # Validate Centre Remplisseur exists
        centre = db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.id == schema.centre_remplisseur_id)
        ).scalar_one_or_none()
        
        if not centre or not centre.is_active:
            raise NotFoundException(f"Centre Remplisseur {schema.centre_remplisseur_id} not found or inactive")
        
        # Check for duplicate numero_bl
        existing_bl = db.execute(
            select(BonReceptionRetour).where(BonReceptionRetour.numero_bl == schema.numero_bl)
        ).scalar_one_or_none()
        
        if existing_bl:
            raise DuplicateException(f"Bon de Réception Retour with numero_bl '{schema.numero_bl}' already exists")
        
        # Check for duplicate numero_reception
        existing_reception = db.execute(
            select(BonReceptionRetour).where(BonReceptionRetour.numero_reception == schema.numero_reception)
        ).scalar_one_or_none()
        
        if existing_reception:
            raise DuplicateException(f"Bon de Réception Retour with numero_reception '{schema.numero_reception}' already exists")
        
        # Create Bon de Réception Retour
        bon_data = schema.model_dump()
        bon_data['status'] = BonReceptionRetourStatus.CREATION
        bon_data['date_creation'] = datetime.utcnow()
        bon_data['palette_count'] = 0
        bon_data['palette_acceptees'] = 0
        bon_data['palette_refusees'] = 0
        
        bon = BonReceptionRetour(**bon_data)
        db.add(bon)
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def get_by_id(db: Session, bon_id: UUID) -> BonReceptionRetour:
        """Get BonReceptionRetour by ID with relationships."""
        bon = db.execute(
            select(BonReceptionRetour)
            .options(
                joinedload(BonReceptionRetour.grossiste),
                joinedload(BonReceptionRetour.depot_depart),
                joinedload(BonReceptionRetour.centre_remplisseur),
                joinedload(BonReceptionRetour.controleur),
                joinedload(BonReceptionRetour.magasinier)
            )
            .where(BonReceptionRetour.id == bon_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon de Réception Retour with ID {bon_id} not found")
        
        return bon
    
    @staticmethod
    def get_by_numero_bl(db: Session, numero_bl: str) -> Optional[BonReceptionRetour]:
        """Get BonReceptionRetour by numero_bl."""
        return db.execute(
            select(BonReceptionRetour).where(BonReceptionRetour.numero_bl == numero_bl)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        grossiste_id: Optional[UUID] = None,
        centre_id: Optional[UUID] = None,
        status: Optional[BonReceptionRetourStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> List[BonReceptionRetour]:
        """Get all BonReceptionRetours with filtering."""
        query = select(BonReceptionRetour)
        
        if grossiste_id:
            query = query.where(BonReceptionRetour.grossiste_id == grossiste_id)
        
        if centre_id:
            query = query.where(BonReceptionRetour.centre_remplisseur_id == centre_id)
        
        if status:
            query = query.where(BonReceptionRetour.status == status)
        
        if date_from:
            query = query.where(BonReceptionRetour.date_creation >= date_from)
        
        if date_to:
            query = query.where(BonReceptionRetour.date_creation <= date_to)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (BonReceptionRetour.numero_bl.ilike(search_pattern)) |
                (BonReceptionRetour.numero_reception.ilike(search_pattern)) |
                (BonReceptionRetour.transporteur_nom.ilike(search_pattern)) |
                (BonReceptionRetour.vehicule_immatriculation.ilike(search_pattern))
            )
        
        query = query.order_by(BonReceptionRetour.date_creation.desc()).offset(skip).limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def update(db: Session, bon_id: UUID, schema: BonReceptionRetourUpdate) -> BonReceptionRetour:
        """
        Update BonReceptionRetour (only editable fields).
        
        Can only update if status is CREATION.
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.CREATION:
            raise BusinessRuleException("Can only update Bon in CREATION status")
        
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bon, field, value)
        
        db.commit()
        db.refresh(bon)
        return bon
    
    @staticmethod
    def depart(
        db: Session,
        bon_id: UUID,
        depart: BonReceptionRetourDepart,
        user_id: UUID
    ) -> BonReceptionRetour:
        """
        Mark departure from depot with palettes.
        
        Status: CREATION -> EN_ROUTE
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.CREATION:
            raise BusinessRuleException(f"Can only depart from CREATION status, current: {bon.status}")
        
        # Validate all palettes exist and are at the depot
        for palette_id in depart.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            if not palette:
                raise NotFoundException(f"Palette {palette_id} not found")
            
            if not palette.can_be_returned():
                raise BusinessRuleException(
                    f"Palette {palette_id} not available for return (status: {palette.status}, full: {palette.is_full})"
                )
            
            # Verify palette is at the departure depot
            if palette.current_depot_id != bon.depot_depart_id:
                raise BusinessRuleException(f"Palette {palette_id} is not at depot {bon.depot_depart_id}")
        
        # Update Bon
        bon.status = BonReceptionRetourStatus.EN_ROUTE
        bon.date_depart = depart.date_depart or datetime.utcnow()
        bon.palette_count = len(depart.palette_ids)
        
        if depart.observations:
            bon.observations = depart.observations
        
        # Update palettes
        for palette_id in depart.palette_ids:
            palette = db.execute(
                select(Palette).where(Palette.id == palette_id)
            ).scalar_one_or_none()
            
            old_status = palette.status
            palette.status = PaletteStatus.EN_ROUTE_RETOUR
            palette.bon_retour_actuel_id = bon.id
            palette.current_depot_id = None  # No longer at depot
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_reception_retour_id=bon.id,
                depot_id=bon.depot_depart_id,
                user_id=user_id,
                action=MovementAction.DEPART_DEPOT,
                status_before=old_status.value,
                status_after=PaletteStatus.EN_ROUTE_RETOUR.value,
                timestamp=bon.date_depart,
                notes=f"Départ retour - Bon {bon.numero_bl}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def marquer_arrivee(
        db: Session,
        bon_id: UUID,
        arrivee: BonReceptionRetourArrivee
    ) -> BonReceptionRetour:
        """
        Mark arrival at Centre Remplisseur.
        
        Status: EN_ROUTE -> ARRIVE
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.EN_ROUTE:
            raise BusinessRuleException(f"Can only mark arrival from EN_ROUTE status, current: {bon.status}")
        
        # Verify magasinier exists
        magasinier = db.execute(
            select(User).where(User.id == arrivee.magasinier_id)
        ).scalar_one_or_none()
        
        if not magasinier:
            raise NotFoundException(f"Magasinier with ID {arrivee.magasinier_id} not found")
        
        # Update Bon
        bon.status = BonReceptionRetourStatus.ARRIVE
        bon.date_arrivee = arrivee.date_arrivee or datetime.utcnow()
        bon.magasinier_id = arrivee.magasinier_id
        bon.magasinier_signature = arrivee.magasinier_signature
        
        if arrivee.observations:
            bon.observations = arrivee.observations
        
        # Update palettes to ARRIVE status
        palettes = db.execute(
            select(Palette).where(Palette.bon_retour_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.AU_CENTRE  # Temporarily, will be EN_CONTROLE after quality check
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_reception_retour_id=bon.id,
                centre_remplisseur_id=bon.centre_remplisseur_id,
                user_id=arrivee.magasinier_id,
                action=MovementAction.ARRIVEE_CENTRE,
                status_before=old_status.value,
                status_after=PaletteStatus.AU_CENTRE.value,
                timestamp=bon.date_arrivee,
                notes=f"Arrivée centre - Bon {bon.numero_bl}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def controle_qualite(
        db: Session,
        bon_id: UUID,
        controle: BonReceptionRetourControle
    ) -> BonReceptionRetour:
        """
        Perform quality control on returned items.
        
        Status: ARRIVE -> EN_CONTROLE
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.ARRIVE:
            raise BusinessRuleException(f"Can only start control from ARRIVE status, current: {bon.status}")
        
        # Verify controleur exists
        controleur = db.execute(
            select(User).where(User.id == controle.controleur_id)
        ).scalar_one_or_none()
        
        if not controleur:
            raise NotFoundException(f"Contrôleur with ID {controle.controleur_id} not found")
        
        # Update Bon
        bon.status = BonReceptionRetourStatus.EN_CONTROLE
        bon.date_controle = controle.date_controle or datetime.utcnow()
        bon.controleur_id = controle.controleur_id
        bon.controleur_signature = controle.controleur_signature
        bon.manquants = controle.manquants
        
        if controle.observations:
            bon.observations = controle.observations
        
        # Create or update DetailRetour records
        palette_acceptees = 0
        palette_refusees = 0
        
        for detail_data in controle.details:
            # Find or create DetailRetour
            detail = DetailRetour(
                bon_reception_retour_id=bon.id,
                type_detail=DetailRetourType(detail_data['type_detail']),
                type_bouteille=detail_data.get('type_bouteille'),
                quantite_prevue=detail_data['quantite_prevue'],
                quantite_recue=detail_data['quantite_recue'],
                quantite_acceptee=detail_data['quantite_acceptee'],
                quantite_refusee=detail_data['quantite_refusee'],
                etat=DetailRetourEtat(detail_data['etat']) if detail_data.get('etat') else None,
                observations=detail_data.get('observations'),
                motif_refus=detail_data.get('motif_refus')
            )
            db.add(detail)
            
            # Update counters (for palettes)
            if detail.type_detail == DetailRetourType.PALETTE_VIDE:
                palette_acceptees += detail.quantite_acceptee
                palette_refusees += detail.quantite_refusee
        
        bon.palette_acceptees = palette_acceptees
        bon.palette_refusees = palette_refusees
        
        # Update palettes to EN_CONTROLE status
        palettes = db.execute(
            select(Palette).where(Palette.bon_retour_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.EN_CONTROLE
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_reception_retour_id=bon.id,
                centre_remplisseur_id=bon.centre_remplisseur_id,
                user_id=controle.controleur_id,
                action=MovementAction.CONTROLE_QUALITE,
                status_before=old_status.value,
                status_after=PaletteStatus.EN_CONTROLE.value,
                timestamp=bon.date_controle,
                notes=f"Contrôle qualité - Bon {bon.numero_bl}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def valider(
        db: Session,
        bon_id: UUID,
        validation: BonReceptionRetourValidation,
        user_id: UUID
    ) -> BonReceptionRetour:
        """
        Validate return reception (all items accepted).
        
        Status: EN_CONTROLE -> VALIDE
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.EN_CONTROLE:
            raise BusinessRuleException(f"Can only validate from EN_CONTROLE status, current: {bon.status}")
        
        # Update Bon
        bon.status = BonReceptionRetourStatus.VALIDE
        bon.date_validation = validation.date_validation or datetime.utcnow()
        bon.client_signature = validation.client_signature
        
        if validation.observations:
            bon.observations = validation.observations
        
        # Update accepted palettes to VALIDEE status
        palettes = db.execute(
            select(Palette).where(Palette.bon_retour_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.VALIDEE
            palette.bon_retour_actuel_id = None  # Return completed
            palette.current_centre_remplisseur_id = bon.centre_remplisseur_id
            palette.is_full = False  # Empty palette returned
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_reception_retour_id=bon.id,
                centre_remplisseur_id=bon.centre_remplisseur_id,
                user_id=user_id,
                action=MovementAction.VALIDATION_RETOUR,
                status_before=old_status.value,
                status_after=PaletteStatus.VALIDEE.value,
                timestamp=bon.date_validation,
                notes=f"Validation retour - Bon {bon.numero_bl}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        return bon
    
    @staticmethod
    def refuser(
        db: Session,
        bon_id: UUID,
        refus: BonReceptionRetourRefus,
        user_id: UUID
    ) -> BonReceptionRetour:
        """
        Refuse return reception (items rejected).
        
        Status: EN_CONTROLE -> REFUSE
        """
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        if bon.status != BonReceptionRetourStatus.EN_CONTROLE:
            raise BusinessRuleException(f"Can only refuse from EN_CONTROLE status, current: {bon.status}")
        
        # Update Bon
        bon.status = BonReceptionRetourStatus.REFUSE
        bon.manquants = refus.motif_refus
        
        if refus.observations:
            bon.observations = refus.observations
        
        # Update palettes - return them to depot status
        palettes = db.execute(
            select(Palette).where(Palette.bon_retour_actuel_id == bon.id)
        ).scalars().all()
        
        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.AU_DEPOT
            palette.bon_retour_actuel_id = None
            palette.current_centre_remplisseur_id = None
            palette.current_depot_id = bon.depot_depart_id  # Back to depot
            
            # Create movement
            movement = PaletteMovement(
                palette_id=palette.id,
                bon_reception_retour_id=bon.id,
                depot_id=bon.depot_depart_id,
                user_id=user_id,
                action=MovementAction.STATUS_CHANGE,
                status_before=old_status.value,
                status_after=PaletteStatus.AU_DEPOT.value,
                notes=f"Retour refusé: {refus.motif_refus}"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(bon)
        
        # TODO: Send notification to grossiste about refusal
        
        return bon
    
    @staticmethod
    def get_with_stats(db: Session, bon_id: UUID) -> dict:
        """Get BonReceptionRetour with statistics."""
        bon = BonReceptionRetourService.get_by_id(db, bon_id)
        
        # Count details
        details_count = db.execute(
            select(func.count()).select_from(BonReceptionRetour).join(
                BonReceptionRetour.details_retour
            ).where(BonReceptionRetour.id == bon.id)
        ).scalar() or 0
        
        # Get names from relationships
        grossiste_name = bon.grossiste.name if bon.grossiste else None
        depot_depart_name = bon.depot_depart.name if bon.depot_depart else None
        centre_name = bon.centre_remplisseur.name if bon.centre_remplisseur else None
        
        # User names
        controleur_name = None
        if bon.controleur:
            controleur_name = f"{bon.controleur.first_name} {bon.controleur.last_name}".strip()
        
        magasinier_name = None
        if bon.magasinier:
            magasinier_name = f"{bon.magasinier.first_name} {bon.magasinier.last_name}".strip()
        
        return {
            "bon": bon,
            "grossiste_name": grossiste_name,
            "depot_depart_name": depot_depart_name,
            "centre_name": centre_name,
            "controleur_name": controleur_name,
            "magasinier_name": magasinier_name,
            "details_count": details_count,
            "taux_acceptation": bon.taux_acceptation,
        }

