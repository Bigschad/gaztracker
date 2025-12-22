"""
Grand Distributeur Service

Business logic for GrandDistributeur operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.grand_distributeur import GrandDistributeur
from app.models.groupe import Groupe
from app.schemas.grand_distributeur import GrandDistributeurCreate, GrandDistributeurUpdate
from app.core.exceptions import NotFoundException, DuplicateException


class GrandDistributeurService:
    """Service for GrandDistributeur operations."""
    
    @staticmethod
    def create(db: Session, schema: GrandDistributeurCreate) -> GrandDistributeur:
        """
        Create a new GrandDistributeur.
        
        Args:
            db: Database session
            schema: GrandDistributeur creation schema
            
        Returns:
            Created GrandDistributeur
            
        Raises:
            NotFoundException: If Groupe not found
            DuplicateException: If code or email already exists
        """
        # Check if Groupe exists
        groupe = db.execute(
            select(Groupe).where(Groupe.id == schema.groupe_id)
        ).scalar_one_or_none()
        
        if not groupe:
            raise NotFoundException("Groupe", schema.groupe_id)
        
        # Check for duplicate code
        existing = db.execute(
            select(GrandDistributeur).where(GrandDistributeur.code == schema.code)
        ).scalar_one_or_none()
        
        if existing:
            raise DuplicateException("GrandDistributeur", "code", schema.code)
        
        # Check for duplicate email if provided
        if schema.email:
            existing_email = db.execute(
                select(GrandDistributeur).where(GrandDistributeur.email == schema.email)
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException("GrandDistributeur", "email", schema.email)
        
        # Create new GrandDistributeur
        grand_distributeur = GrandDistributeur(**schema.model_dump())
        db.add(grand_distributeur)
        db.commit()
        db.refresh(grand_distributeur)
        
        return grand_distributeur
    
    @staticmethod
    def get_by_id(db: Session, grand_distributeur_id: UUID) -> GrandDistributeur:
        """
        Get GrandDistributeur by ID.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            
        Returns:
            GrandDistributeur
            
        Raises:
            NotFoundException: If GrandDistributeur not found
        """
        grand_distributeur = db.execute(
            select(GrandDistributeur).where(GrandDistributeur.id == grand_distributeur_id)
        ).scalar_one_or_none()
        
        if not grand_distributeur:
            raise NotFoundException("GrandDistributeur", grand_distributeur_id)
        
        return grand_distributeur
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[GrandDistributeur]:
        """
        Get GrandDistributeur by code.
        
        Args:
            db: Database session
            code: GrandDistributeur code
            
        Returns:
            GrandDistributeur or None
        """
        return db.execute(
            select(GrandDistributeur).where(GrandDistributeur.code == code)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        groupe_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[GrandDistributeur]:
        """
        Get all GrandDistributeurs with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            groupe_id: Filter by Groupe ID
            is_active: Filter by active status
            search: Search by name or code
            
        Returns:
            List of GrandDistributeurs
        """
        query = select(GrandDistributeur)
        
        # Apply filters
        if groupe_id:
            query = query.where(GrandDistributeur.groupe_id == groupe_id)
        
        if is_active is not None:
            query = query.where(GrandDistributeur.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (GrandDistributeur.name.ilike(search_pattern)) | 
                (GrandDistributeur.code.ilike(search_pattern))
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def count(
        db: Session,
        groupe_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count GrandDistributeurs.
        
        Args:
            db: Database session
            groupe_id: Filter by Groupe ID
            is_active: Filter by active status
            
        Returns:
            Count of GrandDistributeurs
        """
        query = select(func.count(GrandDistributeur.id))
        
        if groupe_id:
            query = query.where(GrandDistributeur.groupe_id == groupe_id)
        
        if is_active is not None:
            query = query.where(GrandDistributeur.is_active == is_active)
        
        return db.execute(query).scalar()
    
    @staticmethod
    def update(
        db: Session,
        grand_distributeur_id: UUID,
        schema: GrandDistributeurUpdate
    ) -> GrandDistributeur:
        """
        Update a GrandDistributeur.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            schema: GrandDistributeur update schema
            
        Returns:
            Updated GrandDistributeur
            
        Raises:
            NotFoundException: If GrandDistributeur or Groupe not found
            DuplicateException: If code or email already exists for another GrandDistributeur
        """
        grand_distributeur = GrandDistributeurService.get_by_id(db, grand_distributeur_id)
        
        # Check if Groupe exists if being updated
        if schema.groupe_id:
            groupe = db.execute(
                select(Groupe).where(Groupe.id == schema.groupe_id)
            ).scalar_one_or_none()
            
            if not groupe:
                raise NotFoundException(f"Groupe with ID {schema.groupe_id} not found")
        
        # Check for duplicate code if being updated
        if schema.code and schema.code != grand_distributeur.code:
            existing = db.execute(
                select(GrandDistributeur).where(
                    (GrandDistributeur.code == schema.code) &
                    (GrandDistributeur.id != grand_distributeur_id)
                )
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException("GrandDistributeur", "code", schema.code)
        
        # Check for duplicate email if being updated
        if schema.email and schema.email != grand_distributeur.email:
            existing_email = db.execute(
                select(GrandDistributeur).where(
                    (GrandDistributeur.email == schema.email) &
                    (GrandDistributeur.id != grand_distributeur_id)
                )
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException("GrandDistributeur", "email", schema.email)
        
        # Update attributes
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grand_distributeur, field, value)
        
        db.commit()
        db.refresh(grand_distributeur)
        
        return grand_distributeur
    
    @staticmethod
    def delete(db: Session, grand_distributeur_id: UUID) -> None:
        """
        Delete a GrandDistributeur.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            
        Raises:
            NotFoundException: If GrandDistributeur not found
        """
        grand_distributeur = GrandDistributeurService.get_by_id(db, grand_distributeur_id)
        
        db.delete(grand_distributeur)
        db.commit()
    
    @staticmethod
    def activate(db: Session, grand_distributeur_id: UUID) -> GrandDistributeur:
        """
        Activate a GrandDistributeur.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            
        Returns:
            Activated GrandDistributeur
            
        Raises:
            NotFoundException: If GrandDistributeur not found
        """
        grand_distributeur = GrandDistributeurService.get_by_id(db, grand_distributeur_id)
        grand_distributeur.is_active = True
        db.commit()
        db.refresh(grand_distributeur)
        return grand_distributeur
    
    @staticmethod
    def deactivate(db: Session, grand_distributeur_id: UUID) -> GrandDistributeur:
        """
        Deactivate a GrandDistributeur.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            
        Returns:
            Deactivated GrandDistributeur
            
        Raises:
            NotFoundException: If GrandDistributeur not found
        """
        grand_distributeur = GrandDistributeurService.get_by_id(db, grand_distributeur_id)
        grand_distributeur.is_active = False
        db.commit()
        db.refresh(grand_distributeur)
        return grand_distributeur
    
    @staticmethod
    def get_with_stats(db: Session, grand_distributeur_id: UUID) -> dict:
        """
        Get GrandDistributeur with statistics.
        
        Args:
            db: Database session
            grand_distributeur_id: GrandDistributeur ID
            
        Returns:
            Dict with GrandDistributeur and statistics
            
        Raises:
            NotFoundException: If GrandDistributeur not found
        """
        grand_distributeur = GrandDistributeurService.get_by_id(db, grand_distributeur_id)
        
        # Count centres remplisseurs
        centres_count = db.execute(
            select(func.count()).select_from(GrandDistributeur).join(
                GrandDistributeur.centres_remplisseurs
            ).where(GrandDistributeur.id == grand_distributeur_id)
        ).scalar() or 0
        
        return {
            "grand_distributeur": grand_distributeur,
            "centres_remplisseurs_count": centres_count,
            "groupe_name": grand_distributeur.groupe.name if grand_distributeur.groupe else None,
        }

