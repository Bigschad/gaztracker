"""
RFID Tag Service

Business logic for managing RFID tags.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import logging
import csv
import io

from app.models.rfid_tag import RFIDTag, RFIDTagStatus
from app.models.user import User
from app.schemas.rfid_tag import RFIDTagCreate, RFIDTagUpdate
from app.utils.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    ValidationException,
)

logger = logging.getLogger(__name__)


class RFIDTagService:
    """Service for managing RFID tags."""

    @staticmethod
    def create_rfid_tag(
        db: Session,
        tag_create: RFIDTagCreate,
        current_user: User
    ) -> RFIDTag:
        """
        Create a new RFID tag.

        Args:
            db: Database session
            tag_create: Tag creation data
            current_user: User creating the tag

        Returns:
            Created RFID tag

        Raises:
            ResourceAlreadyExistsException: If tag_number already exists
        """
        # Check if tag_number already exists
        existing = db.query(RFIDTag).filter(
            RFIDTag.tag_number == tag_create.tag_number
        ).first()

        if existing:
            logger.warning(f"Attempt to create existing tag: {tag_create.tag_number}")
            raise ResourceAlreadyExistsException(
                resource_type="Tag RFID",
                field="tag_number",
                value=tag_create.tag_number,
                message=f"Un tag RFID avec le numéro '{tag_create.tag_number}' existe déjà. Le numéro de tag doit être unique."
            )

        # Create the tag
        new_tag = RFIDTag(
            tag_number=tag_create.tag_number,
            status=RFIDTagStatus.NOT_ASSIGNED,
            created_by_id=current_user.id,
            notes=tag_create.notes,
            is_active=True
        )

        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)

        logger.info(f"RFID tag created: {new_tag.tag_number} by user {current_user.id}")
        return new_tag

    @staticmethod
    def get_rfid_tag(db: Session, tag_id: UUID) -> RFIDTag:
        """
        Get an RFID tag by ID.

        Args:
            db: Database session
            tag_id: Tag UUID

        Returns:
            RFID tag

        Raises:
            ResourceNotFoundException: If tag not found
        """
        tag = db.query(RFIDTag).filter(RFIDTag.id == tag_id).first()
        if not tag:
            raise ResourceNotFoundException(
                resource_type="RFID Tag",
                resource_id=tag_id
            )
        return tag

    @staticmethod
    def get_rfid_tag_by_number(db: Session, tag_number: str) -> RFIDTag:
        """
        Get an RFID tag by its number.

        Args:
            db: Database session
            tag_number: Tag number

        Returns:
            RFID tag

        Raises:
            ResourceNotFoundException: If tag not found
        """
        tag = db.query(RFIDTag).filter(
            RFIDTag.tag_number == tag_number
        ).first()

        if not tag:
            raise ResourceNotFoundException(
                resource_type="RFID Tag",
                resource_id=tag_number,
                message=f"RFID Tag '{tag_number}' not found"
            )
        return tag

    @staticmethod
    def list_rfid_tags(
        db: Session,
        status: Optional[RFIDTagStatus] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RFIDTag], int]:
        """
        List RFID tags with filters and pagination.

        Args:
            db: Database session
            status: Filter by status
            is_active: Filter by active status
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (tags list, total count)
        """
        query = db.query(RFIDTag)

        # Apply filters
        if status:
            query = query.filter(RFIDTag.status == status)
        if is_active is not None:
            query = query.filter(RFIDTag.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        tags = query.order_by(RFIDTag.created_at.desc()).offset(skip).limit(page_size).all()

        logger.info(f"Listed {len(tags)} RFID tags (total: {total})")
        return tags, total

    @staticmethod
    def update_rfid_tag(
        db: Session,
        tag_id: UUID,
        tag_update: RFIDTagUpdate
    ) -> RFIDTag:
        """
        Update an RFID tag.

        Args:
            db: Database session
            tag_id: Tag UUID
            tag_update: Update data

        Returns:
            Updated RFID tag

        Raises:
            ResourceNotFoundException: If tag not found
            ValidationException: If status transition is invalid
        """
        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        # Validate status transition if status is being updated
        if tag_update.status and tag_update.status != tag.status:
            RFIDTagService._validate_status_transition(tag, tag_update.status)

        # Apply updates
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.info(f"RFID tag updated: {tag.tag_number}")
        return tag

    @staticmethod
    def assign_rfid_tag_to_palette(
        db: Session,
        tag_id: UUID,
        palette_id: UUID
    ) -> RFIDTag:
        """
        Assign an RFID tag to a palette.

        Args:
            db: Database session
            tag_id: Tag UUID
            palette_id: Palette UUID

        Returns:
            Updated RFID tag

        Raises:
            ResourceNotFoundException: If tag or palette not found
            ValidationException: If tag is not assignable
        """
        from app.models.palette import Palette

        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        # Verify tag is assignable
        if not tag.is_assignable:
            raise ValidationException(
                message=f"RFID Tag must be NOT_ASSIGNED and active to be assigned (current status: {tag.status})",
                details={
                    "tag_id": str(tag_id),
                    "current_status": tag.status.value,
                    "is_active": tag.is_active
                }
            )

        # Verify palette exists
        palette = db.query(Palette).filter(Palette.id == palette_id).first()
        if not palette:
            raise ResourceNotFoundException(
                resource_type="Palette",
                resource_id=palette_id
            )

        # Assign the tag
        tag.assign_to_palette()
        palette.rfid_tag_id = tag_id

        db.add(tag)
        db.add(palette)
        db.commit()
        db.refresh(tag)

        logger.info(f"RFID tag {tag.tag_number} assigned to palette {palette_id}")
        return tag

    @staticmethod
    def mark_tag_as_lost(db: Session, tag_id: UUID, notes: Optional[str] = None) -> RFIDTag:
        """
        Mark an RFID tag as lost.

        Args:
            db: Database session
            tag_id: Tag UUID
            notes: Optional notes about the loss

        Returns:
            Updated RFID tag
        """
        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        tag.mark_as_lost()
        if notes:
            tag.notes = notes

        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.warning(f"RFID tag marked as lost: {tag.tag_number}")
        return tag

    @staticmethod
    def mark_tag_as_damaged(db: Session, tag_id: UUID, notes: Optional[str] = None) -> RFIDTag:
        """
        Mark an RFID tag as damaged.

        Args:
            db: Database session
            tag_id: Tag UUID
            notes: Optional notes about the damage

        Returns:
            Updated RFID tag
        """
        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        tag.mark_as_damaged()
        if notes:
            tag.notes = notes

        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.warning(f"RFID tag marked as damaged: {tag.tag_number}")
        return tag

    @staticmethod
    def delete_rfid_tag(db: Session, tag_id: UUID) -> bool:
        """
        Delete an RFID tag permanently (hard delete).
        
        Only tags that are NOT_ASSIGNED can be permanently deleted.

        Args:
            db: Database session
            tag_id: Tag UUID

        Returns:
            True if successful

        Raises:
            ResourceNotFoundException: If tag not found
            ValidationException: If tag is assigned to a palette
        """
        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        # Cannot delete assigned tags
        if tag.status == RFIDTagStatus.ASSIGNED:
            raise ValidationException(
                message="Impossible de supprimer définitivement un tag RFID qui est assigné à une palette. Veuillez d'abord désassigner le tag.",
                details={
                    "tag_id": str(tag_id),
                    "tag_number": tag.tag_number,
                    "status": tag.status.value
                }
            )

        # Hard delete - remove from database
        db.delete(tag)
        db.commit()

        logger.info(f"RFID tag permanently deleted: {tag.tag_number}")
        return True

    @staticmethod
    def get_tag_statistics(db: Session) -> dict:
        """
        Get statistics about RFID tags.

        Args:
            db: Database session

        Returns:
            Dictionary with tag statistics
        """
        from sqlalchemy import func

        total_tags = db.query(func.count(RFIDTag.id)).scalar()

        by_status = {}
        for status in RFIDTagStatus:
            count = db.query(func.count(RFIDTag.id)).filter(
                RFIDTag.status == status
            ).scalar()
            by_status[status.value] = count

        active_count = db.query(func.count(RFIDTag.id)).filter(
            RFIDTag.is_active == True
        ).scalar()

        inactive_count = total_tags - active_count

        return {
            "total_tags": total_tags,
            "by_status": by_status,
            "not_assigned": by_status.get("NOT_ASSIGNED", 0),
            "assigned": by_status.get("ASSIGNED", 0),
            "lost": by_status.get("LOST", 0),
            "damaged": by_status.get("DAMAGED", 0),
            "active": active_count,
            "inactive": inactive_count
        }

    @staticmethod
    def _validate_status_transition(tag: RFIDTag, new_status: RFIDTagStatus) -> None:
        """
        Validate if status transition is allowed.

        Args:
            tag: Current RFID tag
            new_status: New status

        Raises:
            ValidationException: If transition is not allowed
        """
        # Define allowed transitions
        allowed_transitions = {
            RFIDTagStatus.NOT_ASSIGNED: [RFIDTagStatus.ASSIGNED, RFIDTagStatus.LOST, RFIDTagStatus.DAMAGED],
            RFIDTagStatus.ASSIGNED: [RFIDTagStatus.NOT_ASSIGNED, RFIDTagStatus.LOST, RFIDTagStatus.DAMAGED],
            RFIDTagStatus.LOST: [RFIDTagStatus.NOT_ASSIGNED, RFIDTagStatus.DAMAGED],
            RFIDTagStatus.DAMAGED: [RFIDTagStatus.NOT_ASSIGNED],
        }

        if new_status not in allowed_transitions.get(tag.status, []):
            raise ValidationException(
                message=f"Cannot transition RFID tag from {tag.status.value} to {new_status.value}",
                details={
                    "tag_number": tag.tag_number,
                    "current_status": tag.status.value,
                    "new_status": new_status.value,
                    "allowed_transitions": [s.value for s in allowed_transitions.get(tag.status, [])]
                }
            )

    @staticmethod
    def bulk_import_tags(
        db: Session,
        csv_content: str,
        current_user: User
    ) -> Dict[str, Any]:
        """
        Import RFID tags in bulk from CSV content.

        CSV format expected:
        - tag_number (required)
        - notes (optional)

        Args:
            db: Database session
            csv_content: CSV file content as string
            current_user: User performing the import

        Returns:
            Dictionary with import results:
            {
                "success": int,
                "failed": int,
                "errors": [{"row": int, "tag_number": str, "error": str}]
            }
        """
        success_count = 0
        failed_count = 0
        errors = []

        try:
            # Parse CSV content
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.DictReader(csv_file)

            # Validate headers
            required_headers = ['tag_number']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                raise ValidationException(
                    message="CSV file must contain 'tag_number' column",
                    details={"found_headers": csv_reader.fieldnames}
                )

            row_num = 1  # Start at 1 (header is row 0)
            for row in csv_reader:
                row_num += 1
                tag_number = row.get('tag_number', '').strip()
                notes = row.get('notes', '').strip() or None

                # Skip empty rows
                if not tag_number:
                    continue

                try:
                    # Check if tag already exists
                    existing = db.query(RFIDTag).filter(
                        RFIDTag.tag_number == tag_number
                    ).first()

                    if existing:
                        errors.append({
                            "row": row_num,
                            "tag_number": tag_number,
                            "error": f"Le numéro de tag '{tag_number}' existe déjà. Le numéro de tag doit être unique."
                        })
                        failed_count += 1
                        continue

                    # Create the tag
                    new_tag = RFIDTag(
                        tag_number=tag_number,
                        status=RFIDTagStatus.NOT_ASSIGNED,
                        created_by_id=current_user.id,
                        notes=notes,
                        is_active=True
                    )

                    db.add(new_tag)
                    success_count += 1

                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "tag_number": tag_number,
                        "error": str(e)
                    })
                    failed_count += 1
                    logger.error(f"Error importing tag {tag_number} at row {row_num}: {str(e)}")

            # Commit all successful imports
            db.commit()
            logger.info(f"Bulk import completed: {success_count} success, {failed_count} failed")

        except ValidationException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk import failed: {str(e)}")
            raise ValidationException(
                message="Failed to process CSV file",
                details={"error": str(e)}
            )

        return {
            "success": success_count,
            "failed": failed_count,
            "errors": errors
        }
