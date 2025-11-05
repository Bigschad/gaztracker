"""
Palette Service

Business logic for palette management including RFID tag integration.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from uuid import UUID
from datetime import datetime
from typing import Optional, Tuple, List
import logging

from app.models.palette import Palette, PaletteStatus, PaletteType
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.rfid_tag import RFIDTag, RFIDTagStatus
from app.models.user import User
from app.schemas.palette import PaletteCreate, PaletteUpdate, PaletteLocationUpdate
from app.services.rfid_tag_service import RFIDTagService
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    PaletteNotAvailableException,
    InvalidStatusTransitionException,
)

logger = logging.getLogger(__name__)


class PaletteService:
    """Service for managing palettes."""

    @staticmethod
    def create_palette(
        db: Session,
        palette_create: PaletteCreate,
        current_user: User
    ) -> Palette:
        """
        Create a new palette and attach an RFID tag.

        Process:
        1. Verify RFID tag exists and is NOT_ASSIGNED
        2. Create the palette
        3. Assign the RFID tag to the palette
        4. Create initial movement history entry

        Args:
            db: Database session
            palette_create: Palette creation data
            current_user: User creating the palette

        Returns:
            Created palette

        Raises:
            ResourceNotFoundException: If RFID tag not found
            ValidationException: If RFID tag is not assignable
        """
        # Get and validate RFID tag
        tag = RFIDTagService.get_rfid_tag(db, palette_create.rfid_tag_id)

        if not tag.is_assignable:
            raise ValidationException(
                message=f"RFID tag must be NOT_ASSIGNED and active (current status: {tag.status})",
                details={
                    "tag_id": str(tag.id),
                    "tag_number": tag.tag_number,
                    "status": tag.status.value,
                    "is_active": tag.is_active
                }
            )

        # Create the palette
        new_palette = Palette(
            type=palette_create.type,
            status=PaletteStatus.CREATION,
            rfid_tag_id=tag.id,
            location_latitude=palette_create.location_latitude,
            location_longitude=palette_create.location_longitude,
            location_address=palette_create.location_address,
            notes=palette_create.notes,
            created_by_id=current_user.id
        )

        # Assign the RFID tag
        tag.assign_to_palette()

        db.add(new_palette)
        db.add(tag)
        db.flush()

        # Create initial movement history
        movement = PaletteMovement(
            palette_id=new_palette.id,
            action=MovementAction.CREATED,
            status_before=None,
            status_after=PaletteStatus.CREATION,
            performed_by_id=current_user.id,
            notes=f"Palette created with RFID tag {tag.tag_number}",
            location_latitude=palette_create.location_latitude,
            location_longitude=palette_create.location_longitude
        )
        db.add(movement)

        db.commit()
        db.refresh(new_palette)

        logger.info(f"Palette created: {new_palette.id} with RFID tag {tag.tag_number}")
        return new_palette

    @staticmethod
    def get_palette(db: Session, palette_id: UUID, include_relations: bool = True) -> Palette:
        """
        Get a palette by ID.

        Args:
            db: Database session
            palette_id: Palette UUID
            include_relations: Whether to load relationships

        Returns:
            Palette

        Raises:
            ResourceNotFoundException: If palette not found
        """
        query = db.query(Palette)

        if include_relations:
            query = query.options(
                joinedload(Palette.rfid_tag),
                joinedload(Palette.created_by)
            )

        palette = query.filter(Palette.id == palette_id).first()

        if not palette:
            raise ResourceNotFoundException(
                resource_type="Palette",
                resource_id=palette_id
            )

        return palette

    @staticmethod
    def get_palette_by_rfid(db: Session, rfid_tag_number: str) -> Palette:
        """
        Get a palette by its RFID tag number.

        Args:
            db: Database session
            rfid_tag_number: RFID tag number

        Returns:
            Palette

        Raises:
            ResourceNotFoundException: If palette not found
        """
        palette = db.query(Palette).join(RFIDTag).filter(
            RFIDTag.tag_number == rfid_tag_number
        ).options(
            joinedload(Palette.rfid_tag),
            joinedload(Palette.created_by)
        ).first()

        if not palette:
            raise ResourceNotFoundException(
                resource_type="Palette",
                resource_id=rfid_tag_number,
                message=f"Palette with RFID tag '{rfid_tag_number}' not found"
            )

        return palette

    @staticmethod
    def list_palettes(
        db: Session,
        palette_type: Optional[PaletteType] = None,
        status: Optional[PaletteStatus] = None,
        created_by_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Palette], int]:
        """
        List palettes with filters and pagination.

        Args:
            db: Database session
            palette_type: Filter by palette type
            status: Filter by status
            created_by_id: Filter by creator
            search: Search in RFID tag number or notes
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (palettes list, total count)
        """
        query = db.query(Palette).options(
            joinedload(Palette.rfid_tag),
            joinedload(Palette.created_by)
        )

        # Apply filters
        if palette_type:
            query = query.filter(Palette.type == palette_type)
        if status:
            query = query.filter(Palette.status == status)
        if created_by_id:
            query = query.filter(Palette.created_by_id == created_by_id)
        if search:
            query = query.join(RFIDTag).filter(
                or_(
                    RFIDTag.tag_number.ilike(f"%{search}%"),
                    Palette.notes.ilike(f"%{search}%")
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        palettes = query.order_by(Palette.created_at.desc()).offset(skip).limit(page_size).all()

        logger.info(f"Listed {len(palettes)} palettes (total: {total})")
        return palettes, total

    @staticmethod
    def update_palette(
        db: Session,
        palette_id: UUID,
        palette_update: PaletteUpdate,
        current_user: User
    ) -> Palette:
        """
        Update a palette.

        Args:
            db: Database session
            palette_id: Palette UUID
            palette_update: Update data
            current_user: User performing the update

        Returns:
            Updated palette

        Raises:
            ResourceNotFoundException: If palette not found
            InvalidStatusTransitionException: If status transition is invalid
        """
        palette = PaletteService.get_palette(db, palette_id)
        old_status = palette.status

        # Validate status transition if status is being updated
        if palette_update.status and palette_update.status != old_status:
            PaletteService._validate_status_transition(palette, palette_update.status)

        # Apply updates
        update_data = palette_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(palette, field, value)

        db.add(palette)

        # Create movement if status changed
        if palette_update.status and old_status != palette_update.status:
            movement = PaletteMovement(
                palette_id=palette_id,
                action=MovementAction.STATUS_CHANGED,
                status_before=old_status,
                status_after=palette_update.status,
                performed_by_id=current_user.id,
                notes=f"Status changed from {old_status.value} to {palette_update.status.value}",
                location_latitude=palette_update.location_latitude,
                location_longitude=palette_update.location_longitude
            )
            db.add(movement)

        db.commit()
        db.refresh(palette)

        logger.info(f"Palette {palette_id} updated")
        return palette

    @staticmethod
    def update_palette_location(
        db: Session,
        palette_id: UUID,
        location_update: PaletteLocationUpdate,
        current_user: User
    ) -> Palette:
        """
        Update palette location.

        Args:
            db: Database session
            palette_id: Palette UUID
            location_update: Location data
            current_user: User performing the update

        Returns:
            Updated palette
        """
        palette = PaletteService.get_palette(db, palette_id)

        palette.update_location(
            latitude=location_update.latitude,
            longitude=location_update.longitude,
            address=location_update.address
        )

        # Create movement entry
        movement = PaletteMovement(
            palette_id=palette_id,
            action=MovementAction.LOCATION_UPDATED,
            status_before=palette.status,
            status_after=palette.status,
            performed_by_id=current_user.id,
            notes="Location updated",
            location_latitude=location_update.latitude,
            location_longitude=location_update.longitude
        )
        db.add(movement)

        db.add(palette)
        db.commit()
        db.refresh(palette)

        logger.info(f"Palette {palette_id} location updated")
        return palette

    @staticmethod
    def get_palette_history(
        db: Session,
        palette_id: UUID
    ) -> List[PaletteMovement]:
        """
        Get complete movement history for a palette.

        Args:
            db: Database session
            palette_id: Palette UUID

        Returns:
            List of movements ordered chronologically

        Raises:
            ResourceNotFoundException: If palette not found
        """
        # Verify palette exists
        _ = PaletteService.get_palette(db, palette_id, include_relations=False)

        movements = db.query(PaletteMovement).filter(
            PaletteMovement.palette_id == palette_id
        ).order_by(PaletteMovement.timestamp.asc()).all()

        return movements

    @staticmethod
    def scan_palette(
        db: Session,
        rfid_tag_number: str,
        current_user: User,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Palette:
        """
        Scan a palette by RFID and record the scan.

        Args:
            db: Database session
            rfid_tag_number: RFID tag number
            current_user: User performing the scan
            latitude: GPS latitude
            longitude: GPS longitude
            notes: Optional scan notes

        Returns:
            Scanned palette

        Raises:
            ResourceNotFoundException: If palette not found
        """
        palette = PaletteService.get_palette_by_rfid(db, rfid_tag_number)

        # Update location if provided
        if latitude and longitude:
            palette.update_location(latitude, longitude)

        # Create movement entry
        movement = PaletteMovement(
            palette_id=palette.id,
            action=MovementAction.SCANNED,
            status_before=palette.status,
            status_after=palette.status,
            performed_by_id=current_user.id,
            notes=notes or f"Palette scanned via RFID: {rfid_tag_number}",
            location_latitude=latitude,
            location_longitude=longitude
        )
        db.add(movement)

        db.add(palette)
        db.commit()
        db.refresh(palette)

        logger.info(f"Palette {palette.id} scanned by user {current_user.id}")
        return palette

    @staticmethod
    def get_palette_statistics(db: Session) -> dict:
        """
        Get statistics about palettes.

        Args:
            db: Database session

        Returns:
            Dictionary with palette statistics
        """
        total_palettes = db.query(func.count(Palette.id)).scalar()

        by_type = {}
        for ptype in PaletteType:
            count = db.query(func.count(Palette.id)).filter(
                Palette.type == ptype
            ).scalar()
            by_type[ptype.value] = count

        by_status = {}
        for pstatus in PaletteStatus:
            count = db.query(func.count(Palette.id)).filter(
                Palette.status == pstatus
            ).scalar()
            by_status[pstatus.value] = count

        return {
            "total_palettes": total_palettes,
            "by_type": by_type,
            "by_status": by_status,
            "in_stock": by_status.get("EN_STOCK", 0),
            "in_transit": by_status.get("EN_ROUTE", 0),
            "delivered": by_status.get("LIVREE", 0)
        }

    @staticmethod
    def _validate_status_transition(palette: Palette, new_status: PaletteStatus) -> None:
        """
        Validate if status transition is allowed.

        Args:
            palette: Current palette
            new_status: New status

        Raises:
            InvalidStatusTransitionException: If transition is not allowed
        """
        # Define allowed transitions
        allowed_transitions = {
            PaletteStatus.CREATION: [PaletteStatus.EN_STOCK, PaletteStatus.OUT],
            PaletteStatus.EN_STOCK: [PaletteStatus.EN_ROUTE, PaletteStatus.OUT],
            PaletteStatus.EN_ROUTE: [PaletteStatus.EN_RECEPTION, PaletteStatus.EN_STOCK],
            PaletteStatus.EN_RECEPTION: [PaletteStatus.LIVREE, PaletteStatus.EN_ROUTE],
            PaletteStatus.LIVREE: [PaletteStatus.RETOURNEE, PaletteStatus.OUT],
            PaletteStatus.RETOURNEE: [PaletteStatus.EN_STOCK, PaletteStatus.OUT],
            PaletteStatus.OUT: [],  # Terminal state
        }

        if new_status not in allowed_transitions.get(palette.status, []):
            raise InvalidStatusTransitionException(
                current_status=palette.status.value,
                new_status=new_status.value,
                resource_type="Palette"
            )
