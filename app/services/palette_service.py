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
import re

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
    def _generate_serial_number(db: Session) -> str:
        """
        Generate a unique serial number for a new palette.

        Format: PAL-YYYY-NNNNN where:
        - PAL: Prefix for palette
        - YYYY: Current year
        - NNNNN: Sequential number (5 digits, zero-padded)

        Args:
            db: Database session

        Returns:
            Generated serial number (e.g., "PAL-2025-00001")
        """
        current_year = datetime.now().year
        prefix = f"PAL-{current_year}-"

        # Find the latest serial number for the current year
        latest_palette = db.query(Palette).filter(
            Palette.serial_number.like(f"{prefix}%")
        ).order_by(Palette.serial_number.desc()).first()

        if latest_palette and latest_palette.serial_number:
            # Extract the counter from the last serial number
            match = re.search(r'PAL-\d{4}-(\d{5})', latest_palette.serial_number)
            if match:
                counter = int(match.group(1)) + 1
            else:
                counter = 1
        else:
            counter = 1

        # Generate the new serial number with zero-padding
        serial_number = f"{prefix}{counter:05d}"

        return serial_number

    @staticmethod
    def create_palette(
        db: Session,
        palette_create: PaletteCreate,
        current_user: User
    ) -> Palette:
        """
        Create a new palette and optionally attach an RFID tag.

        Process:
        1. Generate unique serial number
        2. If RFID tag provided: verify it exists and is NOT_ASSIGNED
        3. Create the palette
        4. If RFID tag provided: assign it to the palette
        5. Create initial movement history entry

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
        tag = None
        tag_number = None

        # Get and validate RFID tag if provided
        if palette_create.rfid_tag_id:
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
            tag_number = tag.tag_number

        # Generate unique serial number
        serial_number = PaletteService._generate_serial_number(db)

        # Create the palette
        new_palette = Palette(
            serial_number=serial_number,
            reference_code=palette_create.reference_code,
            type=palette_create.type,
            capacity=palette_create.capacity,
            manufacturing_date=palette_create.manufacturing_date,
            status=PaletteStatus.CREATION,
            rfid_tag_id=tag.id if tag else None,
            current_partner_id=palette_create.current_partner_id,
            location_latitude=palette_create.location_latitude,
            location_longitude=palette_create.location_longitude,
            location_address=palette_create.location_address,
            notes=palette_create.notes,
            created_by_id=current_user.id
        )

        db.add(new_palette)

        # Assign the RFID tag if provided
        if tag:
            tag.assign_to_palette()
            db.add(tag)

        db.flush()

        # Create initial movement history
        notes_text = f"Palette created with RFID tag {tag_number}" if tag_number else "Palette created without RFID tag"
        movement = PaletteMovement(
            palette_id=new_palette.id,
            action=MovementAction.CREATION,
            status_before=None,
            status_after=PaletteStatus.CREATION,
            user_id=current_user.id,
            notes=notes_text,
            latitude=palette_create.location_latitude,
            longitude=palette_create.location_longitude
        )
        db.add(movement)

        db.commit()
        db.refresh(new_palette)

        log_msg = f"Palette created: {new_palette.serial_number} (ID: {new_palette.id})"
        if tag_number:
            log_msg += f" with RFID tag {tag_number}"
        else:
            log_msg += " without RFID tag"
        logger.info(log_msg)

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
                joinedload(Palette.created_by),
                joinedload(Palette.current_partner)
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
            joinedload(Palette.created_by),
            joinedload(Palette.current_partner)
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
            joinedload(Palette.created_by),
            joinedload(Palette.current_partner)
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
            ValidationException: If RFID tag cannot be assigned
        """
        palette = PaletteService.get_palette(db, palette_id)
        old_status = palette.status
        old_rfid_tag = palette.rfid_tag

        # Validate status transition if status is being updated
        if palette_update.status and palette_update.status != old_status:
            PaletteService._validate_status_transition(palette, palette_update.status)

        # Handle RFID tag reassignment if requested
        if palette_update.rfid_tag_id is not None:
            # Get the new tag and validate it
            new_tag = RFIDTagService.get_rfid_tag(db, palette_update.rfid_tag_id)

            if not new_tag.is_assignable:
                raise ValidationException(
                    f"RFID tag {new_tag.tag_number} is not assignable. "
                    f"Status: {new_tag.status}, Active: {new_tag.is_active}"
                )

            # If palette already has a tag, unassign it first
            if old_rfid_tag:
                old_rfid_tag.unassign_from_palette()
                db.add(old_rfid_tag)
                logger.info(f"Unassigned old RFID tag {old_rfid_tag.tag_number} from palette {palette_id}")

            # Assign the new tag
            new_tag.assign_to_palette()
            db.add(new_tag)
            logger.info(f"Assigned new RFID tag {new_tag.tag_number} to palette {palette_id}")

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

        # Create movement if RFID tag changed
        if palette_update.rfid_tag_id is not None and old_rfid_tag:
            movement = PaletteMovement(
                palette_id=palette_id,
                action=MovementAction.STATUS_CHANGED,
                status_before=old_status,
                status_after=palette.status,
                performed_by_id=current_user.id,
                notes=f"RFID tag reassigned from {old_rfid_tag.tag_number} to {palette.rfid_tag.tag_number}",
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
