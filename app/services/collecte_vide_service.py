"""
Collecte Vide Service

Business logic for CollecteVide operations (empty bottle collection).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.collecte_vide import CollecteVide
from app.models.bon_enlevement import BonEnlevement
from app.models.livraison_detail import LivraisonDetail
from app.models.depot import Depot
from app.models.palette import PaletteType
from app.schemas.collecte_vide import CollecteVideCreate, CollecteVideUpdate, CollecteVideBulk
from app.core.exceptions import NotFoundException, ValidationException, BusinessRuleException


class CollecteVideService:
    """Service for CollecteVide operations."""
    
    @staticmethod
    def create(db: Session, schema: CollecteVideCreate, user_name: Optional[str] = None) -> CollecteVide:
        """
        Create a new CollecteVide record.
        
        Args:
            db: Database session
            schema: CollecteVide creation schema
            user_name: Name of user creating the collecte (usually driver)
            
        Returns:
            Created CollecteVide
            
        Raises:
            NotFoundException: If BonEnlevement, LivraisonDetail, or Depot not found
            ValidationException: If validation fails
        """
        # Validate BonEnlevement exists
        bon = db.execute(
            select(BonEnlevement).where(BonEnlevement.id == schema.bon_enlevement_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon d'Enlèvement {schema.bon_enlevement_id} not found")
        
        # Validate LivraisonDetail if provided
        if schema.livraison_detail_id:
            livraison = db.execute(
                select(LivraisonDetail).where(LivraisonDetail.id == schema.livraison_detail_id)
            ).scalar_one_or_none()
            
            if not livraison:
                raise NotFoundException(f"LivraisonDetail {schema.livraison_detail_id} not found")
            
            if livraison.bon_enlevement_id != schema.bon_enlevement_id:
                raise ValidationException("LivraisonDetail doesn't belong to this Bon d'Enlèvement")
        
        # Validate Depot if provided
        if schema.depot_id:
            depot = db.execute(
                select(Depot).where(Depot.id == schema.depot_id)
            ).scalar_one_or_none()
            
            if not depot:
                raise NotFoundException(f"Depot {schema.depot_id} not found")
        
        # Create CollecteVide
        collecte_data = schema.model_dump()
        
        # Set date_collecte if not provided
        if 'date_collecte' not in collecte_data or collecte_data['date_collecte'] is None:
            collecte_data['date_collecte'] = datetime.utcnow()
        
        # Set collecteur_nom if provided
        if user_name and not collecte_data.get('collecteur_nom'):
            collecte_data['collecteur_nom'] = user_name
        
        collecte = CollecteVide(**collecte_data)
        
        db.add(collecte)
        db.commit()
        db.refresh(collecte)
        
        return collecte
    
    @staticmethod
    def create_bulk(db: Session, bulk: CollecteVideBulk, user_name: Optional[str] = None) -> List[CollecteVide]:
        """
        Create multiple CollecteVide records at once.
        
        Useful for collecting multiple bottle types at once.
        
        Args:
            db: Database session
            bulk: Bulk creation schema
            user_name: Name of user creating the collectes
            
        Returns:
            List of created CollecteVides
        """
        # Validate BonEnlevement exists
        bon = db.execute(
            select(BonEnlevement).where(BonEnlevement.id == bulk.bon_enlevement_id)
        ).scalar_one_or_none()
        
        if not bon:
            raise NotFoundException(f"Bon d'Enlèvement {bulk.bon_enlevement_id} not found")
        
        # Validate LivraisonDetail if provided
        if bulk.livraison_detail_id:
            livraison = db.execute(
                select(LivraisonDetail).where(LivraisonDetail.id == bulk.livraison_detail_id)
            ).scalar_one_or_none()
            
            if not livraison:
                raise NotFoundException(f"LivraisonDetail {bulk.livraison_detail_id} not found")
        
        # Validate Depot if provided
        if bulk.depot_id:
            depot = db.execute(
                select(Depot).where(Depot.id == bulk.depot_id)
            ).scalar_one_or_none()
            
            if not depot:
                raise NotFoundException(f"Depot {bulk.depot_id} not found")
        
        # Create collectes
        created_collectes = []
        
        for collection_data in bulk.collections:
            collecte = CollecteVide(
                bon_enlevement_id=bulk.bon_enlevement_id,
                livraison_detail_id=bulk.livraison_detail_id,
                depot_id=bulk.depot_id,
                type_bouteille=PaletteType(collection_data['type_bouteille']),
                quantite_bouteilles_vides=collection_data.get('quantite_bouteilles_vides', 0),
                quantite_palettes_vides=collection_data.get('quantite_palettes_vides', 0),
                date_collecte=datetime.utcnow(),
                collecteur_nom=user_name or bulk.collecteur_nom,
                observations=collection_data.get('observations')
            )
            db.add(collecte)
            created_collectes.append(collecte)
        
        db.commit()
        
        for collecte in created_collectes:
            db.refresh(collecte)
        
        return created_collectes
    
    @staticmethod
    def get_by_id(db: Session, collecte_id: UUID) -> CollecteVide:
        """Get CollecteVide by ID."""
        collecte = db.execute(
            select(CollecteVide).where(CollecteVide.id == collecte_id)
        ).scalar_one_or_none()
        
        if not collecte:
            raise NotFoundException(f"CollecteVide {collecte_id} not found")
        
        return collecte
    
    @staticmethod
    def get_all_for_bon(db: Session, bon_id: UUID) -> List[CollecteVide]:
        """Get all collectes for a Bon d'Enlèvement."""
        result = db.execute(
            select(CollecteVide)
            .where(CollecteVide.bon_enlevement_id == bon_id)
            .order_by(CollecteVide.date_collecte)
        )
        return list(result.scalars().all())
    
    @staticmethod
    def get_all_for_livraison(db: Session, livraison_id: UUID) -> List[CollecteVide]:
        """Get all collectes for a LivraisonDetail."""
        result = db.execute(
            select(CollecteVide)
            .where(CollecteVide.livraison_detail_id == livraison_id)
            .order_by(CollecteVide.date_collecte)
        )
        return list(result.scalars().all())
    
    @staticmethod
    def get_all_for_depot(
        db: Session,
        depot_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[CollecteVide]:
        """Get all collectes for a Depot with optional date filtering."""
        query = select(CollecteVide).where(CollecteVide.depot_id == depot_id)
        
        if date_from:
            query = query.where(CollecteVide.date_collecte >= date_from)
        
        if date_to:
            query = query.where(CollecteVide.date_collecte <= date_to)
        
        query = query.order_by(CollecteVide.date_collecte.desc())
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def update(db: Session, collecte_id: UUID, schema: CollecteVideUpdate) -> CollecteVide:
        """
        Update CollecteVide.
        
        Typically used to correct quantities or add observations.
        """
        collecte = CollecteVideService.get_by_id(db, collecte_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collecte, field, value)
        
        db.commit()
        db.refresh(collecte)
        
        return collecte
    
    @staticmethod
    def delete(db: Session, collecte_id: UUID) -> None:
        """
        Delete a CollecteVide.
        
        Should be used with caution, typically only for corrections.
        """
        collecte = CollecteVideService.get_by_id(db, collecte_id)
        
        db.delete(collecte)
        db.commit()
    
    @staticmethod
    def get_statistics_by_type(
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        depot_id: Optional[UUID] = None
    ) -> dict:
        """
        Get collection statistics grouped by bottle type.
        
        Returns:
            Dict with statistics per bottle type
        """
        query = select(
            CollecteVide.type_bouteille,
            func.sum(CollecteVide.quantite_bouteilles_vides).label('total_bouteilles'),
            func.sum(CollecteVide.quantite_palettes_vides).label('total_palettes'),
            func.count(CollecteVide.id).label('nb_collectes')
        ).group_by(CollecteVide.type_bouteille)
        
        if date_from:
            query = query.where(CollecteVide.date_collecte >= date_from)
        
        if date_to:
            query = query.where(CollecteVide.date_collecte <= date_to)
        
        if depot_id:
            query = query.where(CollecteVide.depot_id == depot_id)
        
        result = db.execute(query)
        rows = result.all()
        
        stats = {}
        for row in rows:
            stats[row.type_bouteille.value] = {
                "total_bouteilles": row.total_bouteilles or 0,
                "total_palettes": row.total_palettes or 0,
                "nb_collectes": row.nb_collectes or 0
            }
        
        # Calculate totals
        total_bouteilles = sum(s['total_bouteilles'] for s in stats.values())
        total_palettes = sum(s['total_palettes'] for s in stats.values())
        total_collectes = sum(s['nb_collectes'] for s in stats.values())
        
        return {
            "by_type": stats,
            "totals": {
                "total_bouteilles": total_bouteilles,
                "total_palettes": total_palettes,
                "total_collectes": total_collectes
            }
        }
    
    @staticmethod
    def get_summary_for_bon(db: Session, bon_id: UUID) -> dict:
        """
        Get summary of all collectes for a Bon d'Enlèvement.
        
        Returns:
            Dict with summary statistics
        """
        collectes = CollecteVideService.get_all_for_bon(db, bon_id)
        
        if not collectes:
            return {
                "total_collectes": 0,
                "total_bouteilles": 0,
                "total_palettes": 0,
                "by_type": {}
            }
        
        # Group by type
        by_type = {}
        total_bouteilles = 0
        total_palettes = 0
        
        for collecte in collectes:
            type_key = collecte.type_bouteille.value
            
            if type_key not in by_type:
                by_type[type_key] = {
                    "quantite_bouteilles": 0,
                    "quantite_palettes": 0,
                    "nb_collectes": 0
                }
            
            by_type[type_key]["quantite_bouteilles"] += collecte.quantite_bouteilles_vides
            by_type[type_key]["quantite_palettes"] += collecte.quantite_palettes_vides
            by_type[type_key]["nb_collectes"] += 1
            
            total_bouteilles += collecte.quantite_bouteilles_vides
            total_palettes += collecte.quantite_palettes_vides
        
        return {
            "total_collectes": len(collectes),
            "total_bouteilles": total_bouteilles,
            "total_palettes": total_palettes,
            "by_type": by_type
        }

