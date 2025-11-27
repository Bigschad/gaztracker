"""
Depot Service

Business logic for Depot operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.depot import Depot
from app.models.partner import Partner
from app.schemas.depot import DepotCreate, DepotUpdate
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


class DepotService:
    """Service for Depot operations."""
    
    @staticmethod
    def create(db: Session, schema: DepotCreate) -> Depot:
        """
        Create a new Depot.
        
        Args:
            db: Database session
            schema: Depot creation schema
            
        Returns:
            Created Depot
            
        Raises:
            NotFoundException: If Partner not found
            DuplicateException: If code already exists
            ValidationException: If validation fails
        """
        # Check if Partner exists
        partner = db.execute(
            select(Partner).where(Partner.id == schema.partner_id)
        ).scalar_one_or_none()
        
        if not partner:
            raise NotFoundException(f"Partner with ID {schema.partner_id} not found")
        
        # Check for duplicate code if provided
        if schema.code:
            existing = db.execute(
                select(Depot).where(Depot.code == schema.code)
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException(f"Depot with code '{schema.code}' already exists")
        
        # If this is set as main depot, unset any existing main depot for this partner
        if schema.is_main_depot:
            existing_main = db.execute(
                select(Depot).where(
                    (Depot.partner_id == schema.partner_id) &
                    (Depot.is_main_depot == True)
                )
            ).scalar_one_or_none()
            
            if existing_main:
                existing_main.is_main_depot = False
        
        # Create new Depot
        depot = Depot(**schema.model_dump())
        db.add(depot)
        db.commit()
        db.refresh(depot)
        
        return depot
    
    @staticmethod
    def get_by_id(db: Session, depot_id: UUID) -> Depot:
        """
        Get Depot by ID.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Returns:
            Depot
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = db.execute(
            select(Depot).where(Depot.id == depot_id)
        ).scalar_one_or_none()
        
        if not depot:
            raise NotFoundException(f"Depot with ID {depot_id} not found")
        
        return depot
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Depot]:
        """
        Get Depot by code.
        
        Args:
            db: Database session
            code: Depot code
            
        Returns:
            Depot or None
        """
        return db.execute(
            select(Depot).where(Depot.code == code)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        partner_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        is_main_depot: Optional[bool] = None,
        city: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Depot]:
        """
        Get all Depots with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            partner_id: Filter by Partner ID
            is_active: Filter by active status
            is_main_depot: Filter by main depot status
            city: Filter by city
            search: Search by name or code
            
        Returns:
            List of Depots
        """
        query = select(Depot)
        
        # Apply filters
        if partner_id:
            query = query.where(Depot.partner_id == partner_id)
        
        if is_active is not None:
            query = query.where(Depot.is_active == is_active)
        
        if is_main_depot is not None:
            query = query.where(Depot.is_main_depot == is_main_depot)
        
        if city:
            query = query.where(Depot.city.ilike(f"%{city}%"))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Depot.name.ilike(search_pattern)) | 
                (Depot.code.ilike(search_pattern))
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
        Count Depots.
        
        Args:
            db: Database session
            partner_id: Filter by Partner ID
            is_active: Filter by active status
            
        Returns:
            Count of Depots
        """
        query = select(func.count(Depot.id))
        
        if partner_id:
            query = query.where(Depot.partner_id == partner_id)
        
        if is_active is not None:
            query = query.where(Depot.is_active == is_active)
        
        return db.execute(query).scalar()
    
    @staticmethod
    def update(
        db: Session,
        depot_id: UUID,
        schema: DepotUpdate
    ) -> Depot:
        """
        Update a Depot.
        
        Args:
            db: Database session
            depot_id: Depot ID
            schema: Depot update schema
            
        Returns:
            Updated Depot
            
        Raises:
            NotFoundException: If Depot or Partner not found
            DuplicateException: If code already exists for another Depot
        """
        depot = DepotService.get_by_id(db, depot_id)
        
        # Check if Partner exists if being updated
        if schema.partner_id:
            partner = db.execute(
                select(Partner).where(Partner.id == schema.partner_id)
            ).scalar_one_or_none()
            
            if not partner:
                raise NotFoundException(f"Partner with ID {schema.partner_id} not found")
        
        # Check for duplicate code if being updated
        if schema.code and schema.code != depot.code:
            existing = db.execute(
                select(Depot).where(
                    (Depot.code == schema.code) &
                    (Depot.id != depot_id)
                )
            ).scalar_one_or_none()
            
            if existing:
                raise DuplicateException(f"Depot with code '{schema.code}' already exists")
        
        # If setting as main depot, unset any existing main depot for this partner
        if schema.is_main_depot and not depot.is_main_depot:
            partner_id_to_check = schema.partner_id if schema.partner_id else depot.partner_id
            existing_main = db.execute(
                select(Depot).where(
                    (Depot.partner_id == partner_id_to_check) &
                    (Depot.is_main_depot == True) &
                    (Depot.id != depot_id)
                )
            ).scalar_one_or_none()
            
            if existing_main:
                existing_main.is_main_depot = False
        
        # Update attributes
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(depot, field, value)
        
        db.commit()
        db.refresh(depot)
        
        return depot
    
    @staticmethod
    def delete(db: Session, depot_id: UUID) -> None:
        """
        Delete a Depot.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = DepotService.get_by_id(db, depot_id)
        
        db.delete(depot)
        db.commit()
    
    @staticmethod
    def activate(db: Session, depot_id: UUID) -> Depot:
        """
        Activate a Depot.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Returns:
            Activated Depot
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = DepotService.get_by_id(db, depot_id)
        depot.is_active = True
        db.commit()
        db.refresh(depot)
        return depot
    
    @staticmethod
    def deactivate(db: Session, depot_id: UUID) -> Depot:
        """
        Deactivate a Depot.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Returns:
            Deactivated Depot
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = DepotService.get_by_id(db, depot_id)
        depot.is_active = False
        db.commit()
        db.refresh(depot)
        return depot
    
    @staticmethod
    def set_as_main(db: Session, depot_id: UUID) -> Depot:
        """
        Set depot as main depot for its partner.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Returns:
            Updated Depot
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = DepotService.get_by_id(db, depot_id)
        
        # Unset any existing main depot for this partner
        existing_main = db.execute(
            select(Depot).where(
                (Depot.partner_id == depot.partner_id) &
                (Depot.is_main_depot == True) &
                (Depot.id != depot_id)
            )
        ).scalar_one_or_none()
        
        if existing_main:
            existing_main.is_main_depot = False
        
        depot.is_main_depot = True
        db.commit()
        db.refresh(depot)
        return depot
    
    @staticmethod
    def get_main_depot(db: Session, partner_id: UUID) -> Optional[Depot]:
        """
        Get main depot for a partner.
        
        Args:
            db: Database session
            partner_id: Partner ID
            
        Returns:
            Main Depot or None
        """
        return db.execute(
            select(Depot).where(
                (Depot.partner_id == partner_id) &
                (Depot.is_main_depot == True)
            )
        ).scalar_one_or_none()
    
    @staticmethod
    def get_with_stats(db: Session, depot_id: UUID) -> dict:
        """
        Get Depot with statistics.
        
        Args:
            db: Database session
            depot_id: Depot ID
            
        Returns:
            Dict with Depot and statistics
            
        Raises:
            NotFoundException: If Depot not found
        """
        depot = DepotService.get_by_id(db, depot_id)
        
        # Count palettes at depot
        from app.models.palette import Palette
        palettes_count = db.execute(
            select(func.count()).select_from(Palette).where(
                Palette.current_depot_id == depot_id
            )
        ).scalar() or 0
        
        # Count livraisons
        from app.models.livraison_detail import LivraisonDetail
        livraisons_count = db.execute(
            select(func.count()).select_from(LivraisonDetail).where(
                LivraisonDetail.depot_id == depot_id
            )
        ).scalar() or 0
        
        # Load partner separately to avoid relationship issues
        from app.models.partner import Partner
        partner = db.execute(
            select(Partner).where(Partner.id == depot.partner_id)
        ).scalar_one_or_none()
        
        return {
            "depot": depot,
            "partner_name": partner.name if partner else None,
            "partner_type": partner.type.value if partner else None,
            "palettes_count": palettes_count,
            "livraisons_count": livraisons_count,
            "total_capacity": depot.total_capacity,
        }
    
    @staticmethod
    def get_by_location(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        is_active: bool = True
    ) -> List[Depot]:
        """
        Get Depots near a location.
        
        Args:
            db: Database session
            latitude: Search latitude
            longitude: Search longitude
            radius_km: Search radius in kilometers
            is_active: Filter by active status
            
        Returns:
            List of nearby Depots
            
        Note:
            This is a simple bounding box search. For production, consider PostGIS.
        """
        # Simple bounding box (approximate)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        import math
        
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        query = select(Depot).where(
            (Depot.latitude.between(latitude - lat_delta, latitude + lat_delta)) &
            (Depot.longitude.between(longitude - lon_delta, longitude + lon_delta))
        )
        
        if is_active:
            query = query.where(Depot.is_active == True)
        
        result = db.execute(query)
        return list(result.scalars().all())

