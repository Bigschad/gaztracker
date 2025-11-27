"""
Groupe Service

Business logic for Groupe operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.groupe import Groupe
from app.schemas.groupe import GroupeCreate, GroupeUpdate
from app.core.exceptions import NotFoundException, DuplicateException


class GroupeService:
    """Service for Groupe operations."""
    
    @staticmethod
    def create(db: Session, schema: GroupeCreate) -> Groupe:
        """
        Create a new Groupe.
        
        Args:
            db: Database session
            schema: Groupe creation schema
            
        Returns:
            Created Groupe
            
        Raises:
            DuplicateException: If code or email already exists
        """
        # Check for duplicate code
        existing = db.execute(
            select(Groupe).where(Groupe.code == schema.code)
        ).scalar_one_or_none()
        
        if existing:
            raise DuplicateException(f"Groupe with code '{schema.code}' already exists")
        
        # Check for duplicate email if provided
        if schema.email:
            existing_email = db.execute(
                select(Groupe).where(Groupe.email == schema.email)
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException(f"Groupe with email '{schema.email}' already exists")
        
        # Create new Groupe
        groupe = Groupe(**schema.model_dump())
        db.add(groupe)
        db.commit()
        db.refresh(groupe)
        
        return groupe
    
    @staticmethod
    def get_by_id(db: Session, groupe_id: UUID) -> Groupe:
        """
        Get Groupe by ID.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            
        Returns:
            Groupe
            
        Raises:
            NotFoundException: If Groupe not found
        """
        groupe = db.execute(
            select(Groupe).where(Groupe.id == groupe_id)
        ).scalar_one_or_none()
        
        if not groupe:
            raise NotFoundException(f"Groupe with ID {groupe_id} not found")
        
        return groupe
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Groupe]:
        """
        Get Groupe by code.
        
        Args:
            db: Database session
            code: Groupe code
            
        Returns:
            Groupe or None
        """
        return db.execute(
            select(Groupe).where(Groupe.code == code)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Groupe]:
        """
        Get all Groupes with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            search: Search by name or code
            
        Returns:
            List of Groupes
        """
        query = select(Groupe)
        
        # Apply filters
        if is_active is not None:
            query = query.where(Groupe.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Groupe.name.ilike(search_pattern)) | 
                (Groupe.code.ilike(search_pattern))
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def count(db: Session, is_active: Optional[bool] = None) -> int:
        """
        Count Groupes.
        
        Args:
            db: Database session
            is_active: Filter by active status
            
        Returns:
            Count of Groupes
        """
        query = select(func.count(Groupe.id))
        
        if is_active is not None:
            query = query.where(Groupe.is_active == is_active)
        
        return db.execute(query).scalar()
    
    @staticmethod
    def update(db: Session, groupe_id: UUID, schema: GroupeUpdate) -> Groupe:
        """
        Update a Groupe.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            schema: Groupe update schema
            
        Returns:
            Updated Groupe
            
        Raises:
            NotFoundException: If Groupe not found
            DuplicateException: If code or email already exists for another Groupe
        """
        groupe = GroupeService.get_by_id(db, groupe_id)
        
        # Check for duplicate code if being updated
        if schema.code and schema.code != groupe.code:
            existing = db.execute(
                select(Groupe).where(
                    (Groupe.code == schema.code) &
                    (Groupe.id != groupe_id)
                )
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException(f"Groupe with code '{schema.code}' already exists")
        
        # Check for duplicate email if being updated
        if schema.email and schema.email != groupe.email:
            existing_email = db.execute(
                select(Groupe).where(
                    (Groupe.email == schema.email) &
                    (Groupe.id != groupe_id)
                )
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException(f"Groupe with email '{schema.email}' already exists")
        
        # Update attributes
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(groupe, field, value)
        
        db.commit()
        db.refresh(groupe)
        
        return groupe
    
    @staticmethod
    def delete(db: Session, groupe_id: UUID) -> None:
        """
        Delete a Groupe.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            
        Raises:
            NotFoundException: If Groupe not found
        """
        groupe = GroupeService.get_by_id(db, groupe_id)
        
        db.delete(groupe)
        db.commit()
    
    @staticmethod
    def activate(db: Session, groupe_id: UUID) -> Groupe:
        """
        Activate a Groupe.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            
        Returns:
            Activated Groupe
            
        Raises:
            NotFoundException: If Groupe not found
        """
        groupe = GroupeService.get_by_id(db, groupe_id)
        groupe.is_active = True
        db.commit()
        db.refresh(groupe)
        return groupe
    
    @staticmethod
    def deactivate(db: Session, groupe_id: UUID) -> Groupe:
        """
        Deactivate a Groupe.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            
        Returns:
            Deactivated Groupe
            
        Raises:
            NotFoundException: If Groupe not found
        """
        groupe = GroupeService.get_by_id(db, groupe_id)
        groupe.is_active = False
        db.commit()
        db.refresh(groupe)
        return groupe
    
    @staticmethod
    def get_with_stats(db: Session, groupe_id: UUID) -> dict:
        """
        Get Groupe with statistics.
        
        Args:
            db: Database session
            groupe_id: Groupe ID
            
        Returns:
            Dict with Groupe and statistics
            
        Raises:
            NotFoundException: If Groupe not found
        """
        groupe = GroupeService.get_by_id(db, groupe_id)
        
        # Count grand distributeurs
        grand_distributeurs_count = db.execute(
            select(func.count()).select_from(Groupe).join(Groupe.grand_distributeurs).where(Groupe.id == groupe_id)
        ).scalar() or 0
        
        return {
            "groupe": groupe,
            "grand_distributeurs_count": grand_distributeurs_count,
        }

