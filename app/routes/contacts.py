"""
Contact Routes

API endpoints for contact management.
"""

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from app.database import get_sync_db
from app.middleware.auth_middleware import get_current_user_sync
from app.models.user import User, UserRole
from app.models.contact import Contact
from app.models.partner import Partner
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)
from app.middleware.rbac import require_roles
from app.utils.exceptions import ResourceNotFoundException, ValidationException

router = APIRouter()


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
    description="Create a new contact for a partner"
)
def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: Session = Depends(get_sync_db)
) -> ContactResponse:
    """
    Create a new contact.
    
    Args:
        contact_data: Contact creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created contact
    """
    # Verify partner exists
    partner = db.query(Partner).filter(Partner.id == contact_data.partner_id).first()
    if not partner:
        raise ResourceNotFoundException(f"Partenaire avec l'ID {contact_data.partner_id} introuvable")
    
    # If this is set as primary, unset other primary contacts for this partner
    if contact_data.is_primary:
        db.query(Contact).filter(
            Contact.partner_id == contact_data.partner_id,
            Contact.is_primary == True
        ).update({"is_primary": False})
    
    # Create new contact
    new_contact = Contact(**contact_data.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    return ContactResponse.model_validate(new_contact)


@router.get(
    "",
    response_model=ContactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List contacts",
    description="Get a paginated list of contacts"
)
def list_contacts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    partner_id: Optional[UUID] = Query(None, description="Filter by partner ID"),
    is_primary: Optional[bool] = Query(None, description="Filter by primary status"),
    search: Optional[str] = Query(None, description="Search in name, email, phone"),
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_sync_db)
) -> ContactListResponse:
    """
    List contacts with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        partner_id: Filter by partner ID
        is_primary: Filter by primary status
        search: Search term
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of contacts
    """
    query = db.query(Contact)
    
    # Apply filters
    if partner_id:
        query = query.filter(Contact.partner_id == partner_id)
    if is_primary is not None:
        query = query.filter(Contact.is_primary == is_primary)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Contact.first_name.ilike(search_term)) |
            (Contact.last_name.ilike(search_term)) |
            (Contact.email.ilike(search_term)) |
            (Contact.phone.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    contacts = query.order_by(Contact.last_name, Contact.first_name).offset(offset).limit(page_size).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return ContactListResponse(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contact by ID",
    description="Get a specific contact by its ID"
)
def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_sync_db)
) -> ContactResponse:
    """
    Get a contact by ID.
    
    Args:
        contact_id: Contact UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Contact details
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ResourceNotFoundException(f"Contact avec l'ID {contact_id} introuvable")
    
    return ContactResponse.model_validate(contact)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Update contact",
    description="Update an existing contact"
)
def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: Session = Depends(get_sync_db)
) -> ContactResponse:
    """
    Update a contact.
    
    Args:
        contact_id: Contact UUID
        contact_data: Contact update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ResourceNotFoundException(f"Contact avec l'ID {contact_id} introuvable")
    
    update_dict = contact_data.model_dump(exclude_unset=True)
    
    # If partner_id is being changed, verify new partner exists
    if 'partner_id' in update_dict:
        partner = db.query(Partner).filter(Partner.id == update_dict['partner_id']).first()
        if not partner:
            raise ResourceNotFoundException(f"Partenaire avec l'ID {update_dict['partner_id']} introuvable")
    
    # If setting as primary, unset other primary contacts for the partner
    partner_id = update_dict.get('partner_id', contact.partner_id)
    if update_dict.get('is_primary', contact.is_primary):
        db.query(Contact).filter(
            Contact.partner_id == partner_id,
            Contact.id != contact_id,
            Contact.is_primary == True
        ).update({"is_primary": False})
    
    # Update fields
    for field, value in update_dict.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
    description="Delete a contact"
)
def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a contact.
    
    Args:
        contact_id: Contact UUID
        current_user: Current authenticated user
        db: Database session
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ResourceNotFoundException(f"Contact avec l'ID {contact_id} introuvable")
    
    db.delete(contact)
    db.commit()

