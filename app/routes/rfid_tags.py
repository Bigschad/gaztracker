"""
RFID Tags Routes

API endpoints for RFID tag management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import logging
import math

from app.database import get_sync_db
from app.middleware.auth_middleware import get_current_user_sync
from app.models.user import User, UserRole
from app.models.rfid_tag import RFIDTagStatus
from app.schemas.rfid_tag import (
    RFIDTagCreate,
    RFIDTagUpdate,
    RFIDTagResponse,
    RFIDTagDetailResponse,
    RFIDTagListResponse,
    RFIDTagStatistics,
)
from app.services.rfid_tag_service import RFIDTagService
from app.utils.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    ValidationException,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=RFIDTagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new RFID tag",
    description="""
    Create a new RFID tag from mobile or terminal.

    **Authorized roles**: ADMIN, OPERATEUR_USINE

    The tag will be created with status NOT_ASSIGNED and can later be assigned to a palette.
    """,
    responses={
        201: {"description": "RFID tag created successfully"},
        400: {"description": "Tag number already exists"},
        401: {"description": "Unauthorized"},
        403: {"description": "Insufficient permissions"},
    },
)
async def create_rfid_tag(
    tag_create: RFIDTagCreate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Create a new RFID tag."""
    try:
        # Verify permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.OPERATEUR_USINE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN or OPERATEUR_USINE can create RFID tags",
            )

        tag = RFIDTagService.create_rfid_tag(db, tag_create, current_user)
        return tag

    except ResourceAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating RFID tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/number/{tag_number}",
    response_model=RFIDTagDetailResponse,
    summary="Get RFID tag by number",
    description="Retrieve RFID tag information by scanning its tag number.",
    responses={
        200: {"description": "RFID tag found"},
        404: {"description": "RFID tag not found"},
    },
)
async def get_rfid_tag_by_number(
    tag_number: str,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Get an RFID tag by its tag number (for scanning)."""
    try:
        tag = RFIDTagService.get_rfid_tag_by_number(db, tag_number)

        # Add palette_id if tag is assigned
        response_data = RFIDTagDetailResponse.model_validate(tag)
        if tag.palette:
            response_data.palette_id = tag.palette.id

        return response_data

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving RFID tag by number: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/statistics/summary",
    response_model=RFIDTagStatistics,
    summary="Get RFID tag statistics",
    description="Get aggregated statistics about all RFID tags in the system.",
)
async def get_rfid_tag_statistics(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Get RFID tag statistics."""
    try:
        stats = RFIDTagService.get_tag_statistics(db)
        return RFIDTagStatistics(**stats)

    except Exception as e:
        logger.error(f"Error getting RFID tag statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "",
    response_model=RFIDTagListResponse,
    summary="List RFID tags",
    description="""
    List all RFID tags with optional filters and pagination.

    **Filters:**
    - status: Filter by tag status (NOT_ASSIGNED, ASSIGNED, LOST, DAMAGED)
    - is_active: Filter by active status
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    """,
)
async def list_rfid_tags(
    status: Optional[str] = Query(None, description="Filter by tag status (NOT_ASSIGNED, ASSIGNED, LOST, DAMAGED)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """List RFID tags with filters and pagination."""
    try:
        # Convert string status to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = RFIDTagStatus(status.upper())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value: {status}. Must be one of: NOT_ASSIGNED, ASSIGNED, LOST, DAMAGED"
                )
        
        tags, total = RFIDTagService.list_rfid_tags(
            db,
            status=status_enum,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return RFIDTagListResponse(
            items=tags,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            filters={
                "status": status_enum.value if status_enum else None,
                "is_active": is_active,
            },
        )

    except Exception as e:
        logger.error(f"Error listing RFID tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{tag_id}",
    response_model=RFIDTagDetailResponse,
    summary="Get RFID tag by ID",
    description="Retrieve detailed information about a specific RFID tag.",
    responses={
        200: {"description": "RFID tag found"},
        404: {"description": "RFID tag not found"},
    },
)
async def get_rfid_tag(
    tag_id: UUID,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Get an RFID tag by ID."""
    try:
        tag = RFIDTagService.get_rfid_tag(db, tag_id)

        # Add palette_id if tag is assigned
        response_data = RFIDTagDetailResponse.model_validate(tag)
        if tag.palette:
            response_data.palette_id = tag.palette.id

        return response_data

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving RFID tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{tag_id}",
    response_model=RFIDTagResponse,
    summary="Update RFID tag",
    description="""
    Update an RFID tag (status, notes, etc.).

    **Common use cases:**
    - Mark tag as LOST
    - Mark tag as DAMAGED
    - Add notes
    - Deactivate tag

    **Note**: Status transitions are validated. Not all transitions are allowed.
    """,
    responses={
        200: {"description": "RFID tag updated successfully"},
        400: {"description": "Invalid status transition"},
        404: {"description": "RFID tag not found"},
    },
)
async def update_rfid_tag(
    tag_id: UUID,
    tag_update: RFIDTagUpdate,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Update an RFID tag."""
    try:
        tag = RFIDTagService.update_rfid_tag(db, tag_id, tag_update)
        return tag

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating RFID tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/{tag_id}/mark-lost",
    response_model=RFIDTagResponse,
    summary="Mark RFID tag as lost",
    description="Mark an RFID tag as lost with optional notes.",
    responses={
        200: {"description": "Tag marked as lost"},
        404: {"description": "Tag not found"},
    },
)
async def mark_tag_as_lost(
    tag_id: UUID,
    notes: Optional[str] = Query(None, description="Notes about the loss"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Mark an RFID tag as lost."""
    try:
        tag = RFIDTagService.mark_tag_as_lost(db, tag_id, notes)
        return tag

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error marking tag as lost: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/{tag_id}/mark-damaged",
    response_model=RFIDTagResponse,
    summary="Mark RFID tag as damaged",
    description="Mark an RFID tag as damaged with optional notes.",
    responses={
        200: {"description": "Tag marked as damaged"},
        404: {"description": "Tag not found"},
    },
)
async def mark_tag_as_damaged(
    tag_id: UUID,
    notes: Optional[str] = Query(None, description="Notes about the damage"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Mark an RFID tag as damaged."""
    try:
        tag = RFIDTagService.mark_tag_as_damaged(db, tag_id, notes)
        return tag

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error marking tag as damaged: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete RFID tag permanently",
    description="""
    Permanently delete an RFID tag (hard delete).

    **Restrictions**:
    - Cannot delete tags that are ASSIGNED to a palette
    - Only ADMIN users can delete tags
    - Only tags with status NOT_ASSIGNED can be deleted

    **Warning**: This action cannot be undone!
    """,
    responses={
        204: {"description": "Tag deleted successfully"},
        400: {"description": "Cannot delete assigned tag"},
        403: {"description": "Only admin can delete tags"},
        404: {"description": "Tag not found"},
    },
)
async def delete_rfid_tag(
    tag_id: UUID,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Permanently delete an RFID tag (hard delete)."""
    try:
        # Only admin can delete tags
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les administrateurs peuvent supprimer définitivement les tags RFID",
            )

        RFIDTagService.delete_rfid_tag(db, tag_id)
        return None

    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message if hasattr(e, 'message') else str(e),
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message if hasattr(e, 'message') else str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting RFID tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/bulk-import",
    status_code=status.HTTP_200_OK,
    summary="Bulk import RFID tags from CSV",
    description="""
    Import multiple RFID tags from a CSV file.

    **CSV Format:**
    - Required column: tag_number
    - Optional column: notes
    - First row must be the header

    **Example CSV:**
    ```
    tag_number,notes
    RFID-2024-001,Tag from batch A
    RFID-2024-002,Tag from batch B
    ```

    **Authorized roles**: ADMIN, OPERATEUR_USINE
    """,
    responses={
        200: {"description": "Import completed (may include errors)"},
        400: {"description": "Invalid CSV format"},
        401: {"description": "Unauthorized"},
        403: {"description": "Insufficient permissions"},
    },
)
async def bulk_import_rfid_tags(
    file: UploadFile = File(..., description="CSV file to import"),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync),
):
    """Import RFID tags in bulk from a CSV file."""
    try:
        # Verify permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.OPERATEUR_USINE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN or OPERATEUR_USINE can import RFID tags",
            )

        # Verify file is CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file",
            )

        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')

        # Process import
        result = RFIDTagService.bulk_import_tags(db, csv_content, current_user)

        return result

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during bulk import: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during import",
        )
