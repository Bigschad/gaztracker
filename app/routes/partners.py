"""
Partner Routes

API endpoints for partner management.
"""

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from app.database import get_sync_db
from app.middleware.auth_middleware import get_current_user_sync
from app.models.user import User, UserRole
from app.models.partner import Partner, PartnerType
from app.schemas.partner import (
    PartnerCreate,
    PartnerUpdate,
    PartnerResponse,
    PartnerListResponse,
)
from app.middleware.rbac import require_roles
from app.utils.exceptions import ResourceNotFoundException, ValidationException

router = APIRouter()


@router.post(
    "",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new partner",
    description="Create a new partner (grossiste, fournisseur, transporteur, etc.)"
)
def create_partner(
    partner_data: PartnerCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: Session = Depends(get_sync_db)
) -> PartnerResponse:
    """
    Create a new partner.
    
    Args:
        partner_data: Partner creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created partner
    """
    # Check if partner with same name already exists
    existing = db.query(Partner).filter(Partner.name == partner_data.name).first()
    if existing:
        raise ValidationException(f"Un partenaire avec le nom '{partner_data.name}' existe déjà")
    
    # Create new partner
    new_partner = Partner(**partner_data.model_dump())
    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)
    
    return PartnerResponse.model_validate(new_partner)


@router.get(
    "",
    response_model=PartnerListResponse,
    status_code=status.HTTP_200_OK,
    summary="List partners",
    description="Get a paginated list of partners"
)
def list_partners(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by partner type (GROSSISTE, FOURNISSEUR, TRANSPORTEUR, AUTRE)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name, email, phone"),
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_sync_db)
) -> PartnerListResponse:
    """
    List partners with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        type: Filter by partner type
        is_active: Filter by active status
        search: Search term
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of partners
    """
    # Convert string type to enum if provided
    type_enum = None
    if type:
        try:
            type_enum = PartnerType(type.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid partner type value: {type}. Must be one of: GROSSISTE, FOURNISSEUR, TRANSPORTEUR, AUTRE"
            )
    
    query = db.query(Partner)
    
    # Apply filters
    if type_enum:
        query = query.filter(Partner.type == type_enum)
    if is_active is not None:
        query = query.filter(Partner.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Partner.name.ilike(search_term)) |
            (Partner.email.ilike(search_term)) |
            (Partner.phone.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    partners = query.order_by(Partner.name).offset(offset).limit(page_size).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return PartnerListResponse(
        items=[PartnerResponse.model_validate(p) for p in partners],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{partner_id}",
    response_model=PartnerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get partner by ID",
    description="Get a specific partner by its ID"
)
def get_partner(
    partner_id: UUID,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_sync_db)
) -> PartnerResponse:
    """
    Get a partner by ID.
    
    Args:
        partner_id: Partner UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Partner details
    """
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise ResourceNotFoundException(f"Partenaire avec l'ID {partner_id} introuvable")
    
    return PartnerResponse.model_validate(partner)


@router.put(
    "/{partner_id}",
    response_model=PartnerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update partner",
    description="Update an existing partner"
)
def update_partner(
    partner_id: UUID,
    partner_data: PartnerUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: Session = Depends(get_sync_db)
) -> PartnerResponse:
    """
    Update a partner.
    
    Args:
        partner_id: Partner UUID
        partner_data: Partner update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated partner
    """
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise ResourceNotFoundException(f"Partenaire avec l'ID {partner_id} introuvable")
    
    # Check if name change would conflict
    update_dict = partner_data.model_dump(exclude_unset=True)
    if 'name' in update_dict and update_dict['name'] != partner.name:
        existing = db.query(Partner).filter(Partner.name == update_dict['name']).first()
        if existing:
            raise ValidationException(f"Un partenaire avec le nom '{update_dict['name']}' existe déjà")
    
    # Update fields
    for field, value in update_dict.items():
        setattr(partner, field, value)
    
    db.commit()
    db.refresh(partner)
    
    return PartnerResponse.model_validate(partner)


@router.delete(
    "/{partner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete partner",
    description="Delete a partner (soft delete by setting is_active=False)"
)
def delete_partner(
    partner_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a partner (soft delete).
    
    Args:
        partner_id: Partner UUID
        current_user: Current authenticated user
        db: Database session
    """
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise ResourceNotFoundException(f"Partenaire avec l'ID {partner_id} introuvable")
    
    # Soft delete
    partner.is_active = False
    db.commit()

