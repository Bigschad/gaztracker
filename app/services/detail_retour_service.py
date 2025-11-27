"""
Detail Retour Service

Business logic for DetailRetour operations (return detail management).
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.detail_retour import DetailRetour, DetailRetourType, DetailRetourEtat
from app.models.bon_reception_retour import BonReceptionRetour, BonReceptionRetourStatus
from app.models.palette import PaletteType
from app.schemas.detail_retour import (
    DetailRetourCreate,
    DetailRetourUpdate,
    DetailRetourControle,
    DetailRetourBulkCreate
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException
)


class DetailRetourService:
    """Service for DetailRetour operations."""
    
    @staticmethod
    def create(db: Session, schema: DetailRetourCreate) -> DetailRetour:
        """
        Create a new DetailRetour.
        
        Args:
            db: Database session
            schema: DetailRetour creation schema
            
        Returns:
            Created DetailRetour
            
        Raises:
            NotFoundException: If BonReceptionRetour not found
            ValidationException: If validation fails
        """
        # Validate BonReceptionRetour exists
        bon = db.execute(
            select(BonReceptionRetour).where(BonReceptionRetour.id == schema.bon_reception_retour_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon de Réception Retour {schema.bon_reception_retour_id} not found")
        
        # Can only add details if status is CREATION or EN_CONTROLE
        if bon.status not in [BonReceptionRetourStatus.CREATION, BonReceptionRetourStatus.EN_CONTROLE]:
            raise BusinessRuleException(f"Cannot add detail to Bon in status {bon.status}")
        
        # Create DetailRetour
        detail = DetailRetour(**schema.model_dump())
        db.add(detail)
        db.commit()
        db.refresh(detail)
        
        return detail
    
    @staticmethod
    def create_bulk(db: Session, bulk: DetailRetourBulkCreate) -> List[DetailRetour]:
        """
        Create multiple DetailRetours at once.
        
        Used when initializing expected return items.
        """
        # Validate BonReceptionRetour exists
        bon = db.execute(
            select(BonReceptionRetour).where(BonReceptionRetour.id == bulk.bon_reception_retour_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon de Réception Retour {bulk.bon_reception_retour_id} not found")
        
        if bon.status not in [BonReceptionRetourStatus.CREATION]:
            raise BusinessRuleException(f"Cannot add bulk details to Bon in status {bon.status}")
        
        # Create details
        created_details = []
        
        for detail_data in bulk.details:
            detail = DetailRetour(
                bon_reception_retour_id=bulk.bon_reception_retour_id,
                type_detail=DetailRetourType(detail_data['type_detail']),
                type_bouteille=PaletteType(detail_data['type_bouteille']) if detail_data.get('type_bouteille') else None,
                quantite_prevue=detail_data['quantite_prevue'],
                quantite_recue=0,
                quantite_acceptee=0,
                quantite_refusee=0,
                observations=detail_data.get('observations')
            )
            db.add(detail)
            created_details.append(detail)
        
        db.commit()
        
        for detail in created_details:
            db.refresh(detail)
        
        return created_details
    
    @staticmethod
    def get_by_id(db: Session, detail_id: UUID) -> DetailRetour:
        """Get DetailRetour by ID."""
        detail = db.execute(
            select(DetailRetour).where(DetailRetour.id == detail_id)
        ).scalar_one_or_none()
        
        if not detail:
            raise NotFoundException(f"DetailRetour {detail_id} not found")
        
        return detail
    
    @staticmethod
    def get_all_for_bon(db: Session, bon_id: UUID) -> List[DetailRetour]:
        """Get all details for a Bon de Réception Retour."""
        result = db.execute(
            select(DetailRetour)
            .where(DetailRetour.bon_reception_retour_id == bon_id)
            .order_by(DetailRetour.type_detail, DetailRetour.type_bouteille)
        )
        return list(result.scalars().all())
    
    @staticmethod
    def update(db: Session, detail_id: UUID, schema: DetailRetourUpdate) -> DetailRetour:
        """
        Update DetailRetour.
        
        Used during quality control to update quantities and condition.
        """
        detail = DetailRetourService.get_by_id(db, detail_id)
        
        # Verify Bon status allows updates
        bon = detail.bon_reception_retour
        if bon.status not in [BonReceptionRetourStatus.EN_CONTROLE]:
            raise BusinessRuleException(f"Cannot update detail when Bon status is {bon.status}")
        
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(detail, field, value)
        
        db.commit()
        db.refresh(detail)
        
        return detail
    
    @staticmethod
    def apply_controle(db: Session, detail_id: UUID, controle: DetailRetourControle) -> DetailRetour:
        """
        Apply quality control to a DetailRetour.
        
        Used by controleur to update received/accepted/refused quantities.
        """
        detail = DetailRetourService.get_by_id(db, detail_id)
        
        # Verify Bon status
        bon = detail.bon_reception_retour
        if bon.status not in [BonReceptionRetourStatus.ARRIVE, BonReceptionRetourStatus.EN_CONTROLE]:
            raise BusinessRuleException(f"Cannot apply control when Bon status is {bon.status}")
        
        # Validate quantities
        if controle.quantite_acceptee + controle.quantite_refusee != controle.quantite_recue:
            raise ValidationException("Sum of accepted and refused must equal received quantity")
        
        # Update detail
        detail.quantite_recue = controle.quantite_recue
        detail.quantite_acceptee = controle.quantite_acceptee
        detail.quantite_refusee = controle.quantite_refusee
        detail.etat = controle.etat
        
        if controle.observations:
            detail.observations = controle.observations
        
        if controle.motif_refus:
            detail.motif_refus = controle.motif_refus
        
        db.commit()
        db.refresh(detail)
        
        return detail
    
    @staticmethod
    def delete(db: Session, detail_id: UUID) -> None:
        """
        Delete a DetailRetour.
        
        Can only delete if Bon status is CREATION.
        """
        detail = DetailRetourService.get_by_id(db, detail_id)
        
        bon = detail.bon_reception_retour
        if bon.status != BonReceptionRetourStatus.CREATION:
            raise BusinessRuleException(f"Cannot delete detail when Bon status is {bon.status}")
        
        db.delete(detail)
        db.commit()
    
    @staticmethod
    def get_statistics_by_type(
        db: Session,
        bon_id: Optional[UUID] = None,
        type_detail: Optional[DetailRetourType] = None
    ) -> dict:
        """
        Get statistics for DetailRetours.
        
        Can filter by bon_id and/or type_detail.
        """
        query = select(
            DetailRetour.type_detail,
            DetailRetour.type_bouteille,
            func.sum(DetailRetour.quantite_prevue).label('total_prevue'),
            func.sum(DetailRetour.quantite_recue).label('total_recue'),
            func.sum(DetailRetour.quantite_acceptee).label('total_acceptee'),
            func.sum(DetailRetour.quantite_refusee).label('total_refusee'),
            func.count(DetailRetour.id).label('nb_details')
        ).group_by(DetailRetour.type_detail, DetailRetour.type_bouteille)
        
        if bon_id:
            query = query.where(DetailRetour.bon_reception_retour_id == bon_id)
        
        if type_detail:
            query = query.where(DetailRetour.type_detail == type_detail)
        
        result = db.execute(query)
        rows = result.all()
        
        stats = {}
        for row in rows:
            key = f"{row.type_detail.value}_{row.type_bouteille.value if row.type_bouteille else 'N/A'}"
            stats[key] = {
                "type_detail": row.type_detail.value,
                "type_bouteille": row.type_bouteille.value if row.type_bouteille else None,
                "total_prevue": row.total_prevue or 0,
                "total_recue": row.total_recue or 0,
                "total_acceptee": row.total_acceptee or 0,
                "total_refusee": row.total_refusee or 0,
                "nb_details": row.nb_details or 0,
                "taux_reception": (row.total_recue / row.total_prevue * 100) if row.total_prevue else 0,
                "taux_acceptation": (row.total_acceptee / row.total_recue * 100) if row.total_recue else 0,
            }
        
        # Calculate totals
        total_prevue = sum(s['total_prevue'] for s in stats.values())
        total_recue = sum(s['total_recue'] for s in stats.values())
        total_acceptee = sum(s['total_acceptee'] for s in stats.values())
        total_refusee = sum(s['total_refusee'] for s in stats.values())
        
        return {
            "by_type": stats,
            "totals": {
                "total_prevue": total_prevue,
                "total_recue": total_recue,
                "total_acceptee": total_acceptee,
                "total_refusee": total_refusee,
                "taux_reception": (total_recue / total_prevue * 100) if total_prevue else 0,
                "taux_acceptation": (total_acceptee / total_recue * 100) if total_recue else 0,
            }
        }
    
    @staticmethod
    def get_summary_for_bon(db: Session, bon_id: UUID) -> dict:
        """
        Get summary of all details for a Bon de Réception Retour.
        """
        details = DetailRetourService.get_all_for_bon(db, bon_id)
        
        if not details:
            return {
                "total_details": 0,
                "total_items_prevus": 0,
                "total_items_recus": 0,
                "total_items_acceptes": 0,
                "total_items_refuses": 0,
                "taux_reception": 0,
                "taux_acceptation": 0,
                "details_complets": 0,
                "details_incomplets": 0,
            }
        
        total_prevus = sum(d.quantite_prevue for d in details)
        total_recus = sum(d.quantite_recue for d in details)
        total_acceptes = sum(d.quantite_acceptee for d in details)
        total_refuses = sum(d.quantite_refusee for d in details)
        
        complets = sum(1 for d in details if d.is_complete)
        incomplets = len(details) - complets
        
        return {
            "total_details": len(details),
            "total_items_prevus": total_prevus,
            "total_items_recus": total_recus,
            "total_items_acceptes": total_acceptes,
            "total_items_refuses": total_refuses,
            "taux_reception": (total_recus / total_prevus * 100) if total_prevus else 0,
            "taux_acceptation": (total_acceptes / total_recus * 100) if total_recus else 0,
            "details_complets": complets,
            "details_incomplets": incomplets,
        }

