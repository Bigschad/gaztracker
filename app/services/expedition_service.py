"""
Expedition Service

Business logic for expedition management including palette assignment,
OTP validation, and status workflow management.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from uuid import UUID
from datetime import datetime
from typing import Optional, Tuple, List
import logging

from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette import Palette, PaletteStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.user import User
from app.schemas.expedition import (
    ExpeditionCreate,
    ExpeditionUpdate,
    ExpeditionDepartRequest,
    ExpeditionValidateRequest
)
from app.utils.security import generate_otp_with_expiry, generate_expedition_reference
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    PaletteNotAvailableException,
    InvalidStatusTransitionException,
    InvalidOTPException
)

logger = logging.getLogger(__name__)


class ExpeditionService:
    """Service for managing expeditions."""

    @staticmethod
    def create_expedition(
        db: Session,
        expedition_create: ExpeditionCreate,
        current_user: User
    ) -> Expedition:
        """
        Create a new expedition and optionally assign palettes.

        Args:
            db: Database session
            expedition_create: Expedition creation data
            current_user: User creating the expedition

        Returns:
            Created expedition

        Raises:
            ValidationException: If validation fails
            PaletteNotAvailableException: If palettes are not available
        """
        # Generate unique reference number
        reference_number = generate_expedition_reference()

        # Create the expedition
        new_expedition = Expedition(
            reference_number=reference_number,
            status=ExpeditionStatus.CREATION,
            destination_address=expedition_create.destination_address,
            destination_contact=expedition_create.destination_contact,
            destination_phone=expedition_create.destination_phone,
            transporter=expedition_create.transporter,
            vehicle_info=expedition_create.vehicle_info,
            eta=expedition_create.eta,
            notes=expedition_create.notes,
            libelle=expedition_create.libelle,
            grossiste_id=expedition_create.grossiste_id,
            driver_id=expedition_create.driver_id,
            contact_id=expedition_create.contact_id,
            created_by_id=current_user.id
        )

        db.add(new_expedition)
        db.flush()

        # Assign palettes if provided
        if expedition_create.palette_ids:
            ExpeditionService._assign_palettes(
                db,
                new_expedition,
                expedition_create.palette_ids,
                current_user
            )

        db.commit()
        db.refresh(new_expedition)

        logger.info(f"Expedition created: {new_expedition.id} ({new_expedition.reference_number})")
        return new_expedition

    @staticmethod
    def get_expedition(
        db: Session,
        expedition_id: UUID,
        include_relations: bool = True
    ) -> Expedition:
        """
        Get an expedition by ID.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            include_relations: Whether to load relationships

        Returns:
            Expedition

        Raises:
            ResourceNotFoundException: If expedition not found
        """
        query = db.query(Expedition)

        if include_relations:
            query = query.options(
                joinedload(Expedition.created_by),
                joinedload(Expedition.validated_by),
                joinedload(Expedition.grossiste),
                joinedload(Expedition.driver),
                joinedload(Expedition.contact)
            )

        expedition = query.filter(Expedition.id == expedition_id).first()

        if not expedition:
            raise ResourceNotFoundException(
                resource_type="Expedition",
                resource_id=expedition_id
            )

        return expedition

    @staticmethod
    def get_expedition_by_reference(
        db: Session,
        reference_number: str
    ) -> Expedition:
        """
        Get an expedition by reference number.

        Args:
            db: Database session
            reference_number: Expedition reference number

        Returns:
            Expedition

        Raises:
            ResourceNotFoundException: If expedition not found
        """
        expedition = db.query(Expedition).filter(
            Expedition.reference_number == reference_number
        ).first()

        if not expedition:
            raise ResourceNotFoundException(
                resource_type="Expedition",
                resource_id=reference_number,
                message=f"Expedition with reference '{reference_number}' not found"
            )

        return expedition

    @staticmethod
    def list_expeditions(
        db: Session,
        status: Optional[ExpeditionStatus] = None,
        created_by_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Expedition], int]:
        """
        List expeditions with filters and pagination.

        Args:
            db: Database session
            status: Filter by status
            created_by_id: Filter by creator
            search: Search in reference number, transporter, or destination
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (expeditions list, total count)
        """
        query = db.query(Expedition).options(
            joinedload(Expedition.created_by),
            joinedload(Expedition.validated_by),
            joinedload(Expedition.grossiste),
            joinedload(Expedition.driver),
            joinedload(Expedition.contact)
        )

        # Apply filters
        if status:
            query = query.filter(Expedition.status == status)
        if created_by_id:
            query = query.filter(Expedition.created_by_id == created_by_id)
        if search:
            query = query.filter(
                or_(
                    Expedition.reference_number.ilike(f"%{search}%"),
                    Expedition.transporter.ilike(f"%{search}%"),
                    Expedition.destination_address.ilike(f"%{search}%")
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        expeditions = query.order_by(Expedition.date_creation.desc()).offset(skip).limit(page_size).all()

        logger.info(f"Listed {len(expeditions)} expeditions (total: {total})")
        return expeditions, total

    @staticmethod
    def update_expedition(
        db: Session,
        expedition_id: UUID,
        expedition_update: ExpeditionUpdate,
        current_user: User
    ) -> Expedition:
        """
        Update an expedition.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            expedition_update: Update data
            current_user: User performing the update

        Returns:
            Updated expedition

        Raises:
            ResourceNotFoundException: If expedition not found
            ValidationException: If expedition cannot be modified
            InvalidStatusTransitionException: If status transition is invalid
        """
        expedition = ExpeditionService.get_expedition(db, expedition_id)

        # Check if expedition can be modified
        if not expedition.can_be_modified() and expedition_update.status is None:
            raise ValidationException(
                message="Expedition cannot be modified in current status",
                details={"status": expedition.status.value}
            )

        old_status = expedition.status

        # Validate status transition if status is being updated
        if expedition_update.status and expedition_update.status != old_status:
            ExpeditionService._validate_status_transition(expedition, expedition_update.status)

        # Apply updates
        update_data = expedition_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expedition, field, value)

        db.add(expedition)
        db.commit()
        db.refresh(expedition)

        logger.info(f"Expedition {expedition_id} updated")
        return expedition

    @staticmethod
    def assign_palettes(
        db: Session,
        expedition_id: UUID,
        palette_ids: List[UUID],
        current_user: User
    ) -> Expedition:
        """
        Assign palettes to an expedition.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            palette_ids: List of palette IDs to assign
            current_user: User performing the assignment

        Returns:
            Updated expedition

        Raises:
            ResourceNotFoundException: If expedition or palette not found
            ValidationException: If palettes cannot be assigned
        """
        expedition = ExpeditionService.get_expedition(db, expedition_id)

        # Check if palettes can still be added
        if not expedition.can_add_palettes():
            raise ValidationException(
                message="Cannot add palettes to expedition in current status",
                details={"status": expedition.status.value}
            )

        ExpeditionService._assign_palettes(db, expedition, palette_ids, current_user)

        db.commit()
        db.refresh(expedition)

        logger.info(f"Assigned {len(palette_ids)} palettes to expedition {expedition_id}")
        return expedition

    @staticmethod
    def mark_as_departed(
        db: Session,
        expedition_id: UUID,
        depart_request: ExpeditionDepartRequest,
        current_user: User
    ) -> Expedition:
        """
        Mark expedition as departed and generate OTP.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            depart_request: Departure request data
            current_user: User performing the action

        Returns:
            Updated expedition

        Raises:
            ResourceNotFoundException: If expedition not found
            ValidationException: If expedition cannot depart
        """
        expedition = ExpeditionService.get_expedition(db, expedition_id)

        # Validate current status
        if expedition.status not in [ExpeditionStatus.CREEE, ExpeditionStatus.EN_ATTENTE]:
            raise ValidationException(
                message="Expedition must be CREEE or EN_ATTENTE to mark as departed",
                details={"current_status": expedition.status.value}
            )

        # Check if expedition has palettes
        if expedition.palette_count == 0:
            raise ValidationException(
                message="Cannot depart expedition with no palettes",
                details={"expedition_id": str(expedition_id)}
            )

        # Set departure date
        departure_date = depart_request.date_departure or datetime.utcnow()
        expedition.date_departure = departure_date
        expedition.status = ExpeditionStatus.EN_TRANSIT

        # Generate OTP for delivery validation
        otp, otp_expiry = generate_otp_with_expiry(length=6)
        expedition.otp_code = otp
        expedition.otp_expiry = otp_expiry

        # Update all assigned palettes to EN_ROUTE status
        palettes = db.query(Palette).filter(
            Palette.current_expedition_id == expedition_id
        ).all()

        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.EN_ROUTE_LIVRAISON

            # Create movement history
            movement = PaletteMovement(
                palette_id=palette.id,
                expedition_id=expedition_id,
                action=MovementAction.EXPEDITION_DEPARTED,
                status_before=old_status,
                status_after=PaletteStatus.EN_ROUTE_LIVRAISON.value,
                performed_by_id=current_user.id,
                notes=f"Expedition {expedition.reference_number} departed"
            )
            db.add(movement)

        db.add(expedition)
        db.commit()
        db.refresh(expedition)

        logger.info(f"Expedition {expedition_id} marked as departed. OTP generated.")
        return expedition

    @staticmethod
    def validate_delivery(
        db: Session,
        expedition_id: UUID,
        validate_request: ExpeditionValidateRequest,
        current_user: User
    ) -> Expedition:
        """
        Validate expedition delivery with OTP.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            validate_request: Validation request with OTP
            current_user: User performing the validation

        Returns:
            Updated expedition

        Raises:
            ResourceNotFoundException: If expedition not found
            ValidationException: If expedition cannot be validated
            InvalidOTPException: If OTP is invalid
        """
        expedition = ExpeditionService.get_expedition(db, expedition_id)

        # Validate current status
        if expedition.status not in [ExpeditionStatus.EN_TRANSIT, ExpeditionStatus.ARRIVEE]:
            raise ValidationException(
                message="Expedition must be EN_TRANSIT or ARRIVEE to validate",
                details={"current_status": expedition.status.value}
            )

        # Validate OTP
        if not expedition.validate_otp(validate_request.otp_code):
            raise InvalidOTPException(
                message="Invalid or expired OTP code",
                details={"expedition_id": str(expedition_id)}
            )

        # Mark as delivered
        expedition.status = ExpeditionStatus.LIVREE
        expedition.date_delivery = datetime.utcnow()
        expedition.validated_by_id = current_user.id

        if validate_request.notes:
            expedition.notes = (expedition.notes or "") + f"\nDelivery notes: {validate_request.notes}"

        # Update all assigned palettes to LIVREE status
        palettes = db.query(Palette).filter(
            Palette.current_expedition_id == expedition_id
        ).all()

        for palette in palettes:
            old_status = palette.status
            palette.status = PaletteStatus.AU_DEPOT

            # Create movement history
            movement = PaletteMovement(
                palette_id=palette.id,
                expedition_id=expedition_id,
                action=MovementAction.DELIVERED,
                status_before=old_status,
                status_after=PaletteStatus.AU_DEPOT.value,
                performed_by_id=current_user.id,
                notes=f"Expedition {expedition.reference_number} delivered and validated"
            )
            db.add(movement)

        db.add(expedition)
        db.commit()
        db.refresh(expedition)

        logger.info(f"Expedition {expedition_id} validated and marked as delivered")
        return expedition

    @staticmethod
    def cancel_expedition(
        db: Session,
        expedition_id: UUID,
        reason: str,
        current_user: User
    ) -> Expedition:
        """
        Cancel an expedition.

        Args:
            db: Database session
            expedition_id: Expedition UUID
            reason: Cancellation reason
            current_user: User performing the cancellation

        Returns:
            Updated expedition

        Raises:
            ResourceNotFoundException: If expedition not found
            ValidationException: If expedition cannot be cancelled
        """
        expedition = ExpeditionService.get_expedition(db, expedition_id)

        # Check if expedition can be cancelled
        if expedition.is_completed():
            raise ValidationException(
                message="Cannot cancel completed expedition",
                details={"status": expedition.status.value}
            )

        old_status = expedition.status
        expedition.status = ExpeditionStatus.ANNULEE
        expedition.problem_description = reason

        # Release all assigned palettes
        palettes = db.query(Palette).filter(
            Palette.current_expedition_id == expedition_id
        ).all()

        for palette in palettes:
            palette_old_status = palette.status
            palette.status = PaletteStatus.AU_DEPOT
            palette.current_expedition_id = None

            # Create movement history
            movement = PaletteMovement(
                palette_id=palette.id,
                expedition_id=expedition_id,
                action=MovementAction.EXPEDITION_CANCELLED,
                status_before=palette_old_status,
                status_after=PaletteStatus.AU_DEPOT.value,
                performed_by_id=current_user.id,
                notes=f"Expedition {expedition.reference_number} cancelled: {reason}"
            )
            db.add(movement)

        # Update palette count
        expedition.palette_count = 0

        db.add(expedition)
        db.commit()
        db.refresh(expedition)

        logger.info(f"Expedition {expedition_id} cancelled: {reason}")
        return expedition

    @staticmethod
    def get_expedition_statistics(db: Session) -> dict:
        """
        Get statistics about expeditions.

        Args:
            db: Database session

        Returns:
            Dictionary with expedition statistics
        """
        total_expeditions = db.query(func.count(Expedition.id)).scalar()

        by_status = {}
        for status in ExpeditionStatus:
            count = db.query(func.count(Expedition.id)).filter(
                Expedition.status == status
            ).scalar()
            by_status[status.value] = count

        in_transit = by_status.get("EN_TRANSIT", 0)
        delivered = by_status.get("AU_DEPOT", 0)

        # Count delayed expeditions (past ETA and not delivered)
        delayed = db.query(func.count(Expedition.id)).filter(
            and_(
                Expedition.eta < datetime.utcnow(),
                Expedition.status.notin_([ExpeditionStatus.LIVREE, ExpeditionStatus.ANNULEE]),
                Expedition.eta.isnot(None)
            )
        ).scalar()

        return {
            "total_expeditions": total_expeditions,
            "by_status": by_status,
            "in_transit": in_transit,
            "delivered": delivered,
            "delayed": delayed
        }

    @staticmethod
    def _assign_palettes(
        db: Session,
        expedition: Expedition,
        palette_ids: List[UUID],
        current_user: User
    ) -> None:
        """
        Internal method to assign palettes to an expedition.

        Args:
            db: Database session
            expedition: Expedition to assign palettes to
            palette_ids: List of palette IDs
            current_user: User performing the assignment

        Raises:
            ResourceNotFoundException: If palette not found
            PaletteNotAvailableException: If palette is not available
        """
        for palette_id in palette_ids:
            # Get palette
            palette = db.query(Palette).filter(Palette.id == palette_id).first()

            if not palette:
                raise ResourceNotFoundException(
                    resource_type="Palette",
                    resource_id=palette_id
                )

            # Check if palette can be assigned
            if not palette.can_be_assigned():
                raise PaletteNotAvailableException(
                    palette_id=palette_id,
                    current_status=palette.status.value,
                    details={
                        "palette_id": str(palette_id),
                        "current_status": palette.status.value,
                        "current_expedition": str(palette.current_expedition_id) if palette.current_expedition_id else None
                    }
                )

            # Assign palette to expedition
            old_status = palette.status
            palette.current_expedition_id = expedition.id
            palette.status = PaletteStatus.AU_DEPOT  # Keep in stock until departure

            # Create movement history
            movement = PaletteMovement(
                palette_id=palette_id,
                expedition_id=expedition.id,
                action=MovementAction.ASSIGNED_TO_EXPEDITION,
                status_before=old_status,
                status_after=palette.status,
                performed_by_id=current_user.id,
                notes=f"Assigned to expedition {expedition.reference_number}"
            )
            db.add(movement)

        # Update expedition palette count
        expedition.palette_count = len(palette_ids)

    @staticmethod
    def _validate_status_transition(
        expedition: Expedition,
        new_status: ExpeditionStatus
    ) -> None:
        """
        Validate if status transition is allowed.

        Args:
            expedition: Current expedition
            new_status: New status

        Raises:
            InvalidStatusTransitionException: If transition is not allowed
        """
        # Define allowed transitions
        allowed_transitions = {
            ExpeditionStatus.CREATION: [ExpeditionStatus.EN_ATTENTE, ExpeditionStatus.CREEE, ExpeditionStatus.ANNULEE],
            ExpeditionStatus.EN_ATTENTE: [ExpeditionStatus.CREEE, ExpeditionStatus.ANNULEE],
            ExpeditionStatus.CREEE: [ExpeditionStatus.EN_TRANSIT, ExpeditionStatus.ANNULEE],
            ExpeditionStatus.EN_TRANSIT: [ExpeditionStatus.ARRIVEE, ExpeditionStatus.PROBLEME],
            ExpeditionStatus.ARRIVEE: [ExpeditionStatus.LIVREE, ExpeditionStatus.PROBLEME],
            ExpeditionStatus.LIVREE: [],  # Terminal state
            ExpeditionStatus.PROBLEME: [ExpeditionStatus.EN_TRANSIT, ExpeditionStatus.ANNULEE],
            ExpeditionStatus.ANNULEE: [],  # Terminal state
        }

        if new_status not in allowed_transitions.get(expedition.status, []):
            raise InvalidStatusTransitionException(
                current_status=expedition.status.value,
                new_status=new_status.value,
                resource_type="Expedition"
            )
