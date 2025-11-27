"""
Centre Remplisseur Service

Business logic for CentreRemplisseur operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.centre_remplisseur import CentreRemplisseur
from app.models.grand_distributeur import GrandDistributeur
from app.schemas.centre_remplisseur import CentreRemplisseurCreate, CentreRemplisseurUpdate
from app.core.exceptions import NotFoundException, DuplicateException


class CentreRemplisseurService:
    """Service for CentreRemplisseur operations."""
    
    @staticmethod
    def create(db: Session, schema: CentreRemplisseurCreate) -> CentreRemplisseur:
        """
        Create a new CentreRemplisseur.
        
        Args:
            db: Database session
            schema: CentreRemplisseur creation schema
            
        Returns:
            Created CentreRemplisseur
            
        Raises:
            NotFoundException: If GrandDistributeur not found
            DuplicateException: If code or email already exists
        """
        # Check if GrandDistributeur exists
        grand_distributeur = db.execute(
            select(GrandDistributeur).where(GrandDistributeur.id == schema.grand_distributeur_id)
        ).scalar_one_or_none()
        
        if not grand_distributeur:
            raise NotFoundException(f"GrandDistributeur with ID {schema.grand_distributeur_id} not found")
        
        # Check for duplicate code
        existing = db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.code == schema.code)
        ).scalar_one_or_none()
        
        if existing:
            raise DuplicateException(f"CentreRemplisseur with code '{schema.code}' already exists")
        
        # Check for duplicate email if provided
        if schema.email:
            existing_email = db.execute(
                select(CentreRemplisseur).where(CentreRemplisseur.email == schema.email)
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException(f"CentreRemplisseur with email '{schema.email}' already exists")
        
        # Create new CentreRemplisseur
        centre = CentreRemplisseur(**schema.model_dump())
        db.add(centre)
        db.commit()
        db.refresh(centre)
        
        return centre
    
    @staticmethod
    def get_by_id(db: Session, centre_id: UUID) -> CentreRemplisseur:
        """
        Get CentreRemplisseur by ID.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            
        Returns:
            CentreRemplisseur
            
        Raises:
            NotFoundException: If CentreRemplisseur not found
        """
        centre = db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.id == centre_id)
        ).scalar_one_or_none()
        
        if not centre:
            raise NotFoundException(f"CentreRemplisseur with ID {centre_id} not found")
        
        return centre
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[CentreRemplisseur]:
        """
        Get CentreRemplisseur by code.
        
        Args:
            db: Database session
            code: CentreRemplisseur code
            
        Returns:
            CentreRemplisseur or None
        """
        return db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.code == code)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        grand_distributeur_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        city: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[CentreRemplisseur]:
        """
        Get all CentreRemplisseurs with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            grand_distributeur_id: Filter by GrandDistributeur ID
            is_active: Filter by active status
            city: Filter by city
            search: Search by name or code
            
        Returns:
            List of CentreRemplisseurs
        """
        query = select(CentreRemplisseur)
        
        # Apply filters
        if grand_distributeur_id:
            query = query.where(CentreRemplisseur.grand_distributeur_id == grand_distributeur_id)
        
        if is_active is not None:
            query = query.where(CentreRemplisseur.is_active == is_active)
        
        if city:
            query = query.where(CentreRemplisseur.city.ilike(f"%{city}%"))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (CentreRemplisseur.name.ilike(search_pattern)) | 
                (CentreRemplisseur.code.ilike(search_pattern))
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    def count(
        db: Session,
        grand_distributeur_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count CentreRemplisseurs.
        
        Args:
            db: Database session
            grand_distributeur_id: Filter by GrandDistributeur ID
            is_active: Filter by active status
            
        Returns:
            Count of CentreRemplisseurs
        """
        query = select(func.count(CentreRemplisseur.id))
        
        if grand_distributeur_id:
            query = query.where(CentreRemplisseur.grand_distributeur_id == grand_distributeur_id)
        
        if is_active is not None:
            query = query.where(CentreRemplisseur.is_active == is_active)
        
        return db.execute(query).scalar()
    
    @staticmethod
    def update(
        db: Session,
        centre_id: UUID,
        schema: CentreRemplisseurUpdate
    ) -> CentreRemplisseur:
        """
        Update a CentreRemplisseur.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            schema: CentreRemplisseur update schema
            
        Returns:
            Updated CentreRemplisseur
            
        Raises:
            NotFoundException: If CentreRemplisseur or GrandDistributeur not found
            DuplicateException: If code or email already exists for another CentreRemplisseur
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        
        # Check if GrandDistributeur exists if being updated
        if schema.grand_distributeur_id:
            grand_distributeur = db.execute(
                select(GrandDistributeur).where(GrandDistributeur.id == schema.grand_distributeur_id)
            ).scalar_one_or_none()
            
            if not grand_distributeur:
                raise NotFoundException(f"GrandDistributeur with ID {schema.grand_distributeur_id} not found")
        
        # Check for duplicate code if being updated
        if schema.code and schema.code != centre.code:
            existing = db.execute(
                select(CentreRemplisseur).where(
                    (CentreRemplisseur.code == schema.code) &
                    (CentreRemplisseur.id != centre_id)
                )
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException(f"CentreRemplisseur with code '{schema.code}' already exists")
        
        # Check for duplicate email if being updated
        if schema.email and schema.email != centre.email:
            existing_email = db.execute(
                select(CentreRemplisseur).where(
                    (CentreRemplisseur.email == schema.email) &
                    (CentreRemplisseur.id != centre_id)
                )
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException(f"CentreRemplisseur with email '{schema.email}' already exists")
        
        # Update attributes
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(centre, field, value)
        
        db.commit()
        db.refresh(centre)
        
        return centre
    
    @staticmethod
    def delete(db: Session, centre_id: UUID) -> None:
        """
        Delete a CentreRemplisseur.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            
        Raises:
            NotFoundException: If CentreRemplisseur not found
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        
        db.delete(centre)
        db.commit()
    
    @staticmethod
    def activate(db: Session, centre_id: UUID) -> CentreRemplisseur:
        """
        Activate a CentreRemplisseur.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            
        Returns:
            Activated CentreRemplisseur
            
        Raises:
            NotFoundException: If CentreRemplisseur not found
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        centre.is_active = True
        db.commit()
        db.refresh(centre)
        return centre
    
    @staticmethod
    def deactivate(db: Session, centre_id: UUID) -> CentreRemplisseur:
        """
        Deactivate a CentreRemplisseur.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            
        Returns:
            Deactivated CentreRemplisseur
            
        Raises:
            NotFoundException: If CentreRemplisseur not found
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        centre.is_active = False
        db.commit()
        db.refresh(centre)
        return centre
    
    @staticmethod
    def get_with_stats(db: Session, centre_id: UUID) -> dict:
        """
        Get CentreRemplisseur with statistics.
        
        Args:
            db: Database session
            centre_id: CentreRemplisseur ID
            
        Returns:
            Dict with CentreRemplisseur and statistics
            
        Raises:
            NotFoundException: If CentreRemplisseur not found
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        
        # Count bons d'enlèvement
        bons_enlevement_count = db.execute(
            select(func.count()).select_from(CentreRemplisseur).join(
                CentreRemplisseur.bons_enlevement
            ).where(CentreRemplisseur.id == centre_id)
        ).scalar() or 0
        
        # Count bons de réception retour
        bons_retour_count = db.execute(
            select(func.count()).select_from(CentreRemplisseur).join(
                CentreRemplisseur.bons_reception_retour
            ).where(CentreRemplisseur.id == centre_id)
        ).scalar() or 0
        
        return {
            "centre_remplisseur": centre,
            "bons_enlevement_count": bons_enlevement_count,
            "bons_retour_count": bons_retour_count,
            "grand_distributeur_name": centre.grand_distributeur.name if centre.grand_distributeur else None,
            "groupe_name": centre.grand_distributeur.groupe.name if centre.grand_distributeur and centre.grand_distributeur.groupe else None,
        }
    
    @staticmethod
    def get_by_location(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[CentreRemplisseur]:
        """
        Get CentreRemplisseurs near a location.
        
        Args:
            db: Database session
            latitude: Search latitude
            longitude: Search longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby CentreRemplisseurs
            
        Note:
            This is a simple bounding box search. For production, consider PostGIS.
        """
        # Simple bounding box (approximate)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        import math
        
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        query = select(CentreRemplisseur).where(
            (CentreRemplisseur.latitude.between(latitude - lat_delta, latitude + lat_delta)) &
            (CentreRemplisseur.longitude.between(longitude - lon_delta, longitude + lon_delta)) &
            (CentreRemplisseur.is_active == True)
        )
        
        result = db.execute(query)
        return list(result.scalars().all())

