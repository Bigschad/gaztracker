"""
Centre Remplisseur Service

Business logic for CentreRemplisseur operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
import secrets
import string

from app.models.centre_remplisseur import CentreRemplisseur
from app.models.partner import Partner, PartnerType
from app.schemas.centre_remplisseur import CentreRemplisseurCreate, CentreRemplisseurUpdate
from app.core.exceptions import NotFoundException, DuplicateException


class CentreRemplisseurService:
    """Service for CentreRemplisseur operations."""
    
    @staticmethod
    def _generate_code(db: Session) -> str:
        """
        Generate a unique code for a new CentreRemplisseur.
        
        Format: CR-YYYY-NNNNN where:
        - CR: Prefix for Centre Remplisseur
        - YYYY: Current year
        - NNNNN: Sequential number (5 digits, zero-padded)
        
        Args:
            db: Database session
            
        Returns:
            Generated code (e.g., "CR-2025-00001")
        """
        current_year = datetime.now().year
        prefix = f"CR-{current_year}-"
        
        # Find the latest code for the current year
        latest_centre = db.execute(
            select(CentreRemplisseur).where(
                CentreRemplisseur.code.like(f"{prefix}%")
            ).order_by(CentreRemplisseur.code.desc())
        ).scalar_one_or_none()
        
        if latest_centre and latest_centre.code:
            # Extract the counter from the last code
            import re
            match = re.search(r'CR-\d{4}-(\d{5})', latest_centre.code)
            if match:
                counter = int(match.group(1)) + 1
            else:
                counter = 1
        else:
            counter = 1
        
        # Generate the new code with zero-padding
        code = f"{prefix}{counter:05d}"
        
        # Ensure uniqueness (in case of race condition)
        while db.execute(
            select(CentreRemplisseur).where(CentreRemplisseur.code == code)
        ).scalar_one_or_none():
            counter += 1
            code = f"{prefix}{counter:05d}"
        
        return code
    
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
            NotFoundException: If Partner not found or not a distributeur
            DuplicateException: If code or email already exists
        """
        # Check if Partner exists and is a GROSSISTE (distributeur)
        partner = db.execute(
            select(Partner).where(Partner.id == schema.partner_id)
        ).scalar_one_or_none()
        
        if not partner:
            raise NotFoundException(f"Partner with ID {schema.partner_id} not found")
        
        if partner.type != PartnerType.GROSSISTE:
            raise NotFoundException(f"Partner with ID {schema.partner_id} is not a distributeur (GROSSISTE)")
        
        # Generate code if not provided
        code = schema.code
        if not code:
            code = CentreRemplisseurService._generate_code(db)
        else:
            # Check for duplicate code if provided
            existing = db.execute(
                select(CentreRemplisseur).where(CentreRemplisseur.code == code)
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException(f"CentreRemplisseur with code '{code}' already exists")
        
        # Check for duplicate email if provided
        if schema.email:
            existing_email = db.execute(
                select(CentreRemplisseur).where(CentreRemplisseur.email == schema.email)
            ).scalar_one_or_none()
            
            if existing_email:
                raise DuplicateException(f"CentreRemplisseur with email '{schema.email}' already exists")
        
        # Create new CentreRemplisseur
        centre_data = schema.model_dump()
        centre_data['code'] = code
        centre = CentreRemplisseur(**centre_data)
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
        partner_id: Optional[UUID] = None,
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
            partner_id: Filter by Partner ID
            is_active: Filter by active status
            city: Filter by city
            search: Search by name or code
            
        Returns:
            List of CentreRemplisseurs
        """
        query = select(CentreRemplisseur)
        
        # Apply filters
        if partner_id:
            query = query.where(CentreRemplisseur.partner_id == partner_id)
        
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
        partner_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count CentreRemplisseurs.
        
        Args:
            db: Database session
            partner_id: Filter by Partner ID
            is_active: Filter by active status
            
        Returns:
            Count of CentreRemplisseurs
        """
        query = select(func.count(CentreRemplisseur.id))
        
        if partner_id:
            query = query.where(CentreRemplisseur.partner_id == partner_id)
        
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
            NotFoundException: If CentreRemplisseur or Partner not found
            DuplicateException: If code or email already exists for another CentreRemplisseur
        """
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        
        # Check if Partner exists and is a GROSSISTE if being updated
        if schema.partner_id:
            partner = db.execute(
                select(Partner).where(Partner.id == schema.partner_id)
            ).scalar_one_or_none()
            
            if not partner:
                raise NotFoundException(f"Partner with ID {schema.partner_id} not found")
            
            if partner.type != PartnerType.GROSSISTE:
                raise NotFoundException(f"Partner with ID {schema.partner_id} is not a distributeur (GROSSISTE)")
        
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
        from app.models.bon_enlevement import BonEnlevement
        from app.models.bon_reception_retour import BonReceptionRetour
        
        centre = CentreRemplisseurService.get_by_id(db, centre_id)
        
        # Count bons d'enlèvement
        bons_enlevement_count = db.execute(
            select(func.count(BonEnlevement.id)).where(
                BonEnlevement.centre_remplisseur_id == centre_id
            )
        ).scalar() or 0
        
        # Count bons de réception retour
        bons_retour_count = db.execute(
            select(func.count(BonReceptionRetour.id)).where(
                BonReceptionRetour.centre_remplisseur_id == centre_id
            )
        ).scalar() or 0
        
        return {
            "centre_remplisseur": centre,
            "bons_enlevement_count": bons_enlevement_count,
            "bons_retour_count": bons_retour_count,
            "partner_name": centre.partner.name if centre.partner else None,
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

