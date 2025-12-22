"""add_distributeur_to_partner_type

Revision ID: a3b4c5d6e7f8
Revises: f7e8d9c0b1a2
Create Date: 2025-12-04 12:30:00.000000

Add DISTRIBUTEUR value to partner_type enum (replaces FOURNISSEUR).
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'f7e8d9c0b1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add DISTRIBUTEUR to partner_type enum and update existing data."""
    # Add 'DISTRIBUTEUR' value to the existing partner_type enum if it doesn't exist
    # PostgreSQL doesn't support IF NOT EXISTS for ALTER TYPE ADD VALUE, so we use a DO block
    # Note: ALTER TYPE ADD VALUE cannot be rolled back and may require a commit
    # We use a separate connection to ensure the enum value is available
    connection = op.get_bind()
    
    # Check if DISTRIBUTEUR already exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumlabel = 'DISTRIBUTEUR' 
            AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'partner_type')
        )
    """))
    enum_exists = result.scalar()
    
    if not enum_exists:
        # Add the enum value - this cannot be rolled back
        # Note: PostgreSQL doesn't support IF NOT EXISTS for ALTER TYPE ADD VALUE
        # So we check first and only add if it doesn't exist
        connection.execute(text("ALTER TYPE partner_type ADD VALUE 'DISTRIBUTEUR'"))
    
    # Now update existing FOURNISSEUR records to DISTRIBUTEUR
    # Use a safe approach that handles the case where FOURNISSEUR might not exist
    # We cast to text first to avoid enum comparison issues
    connection.execute(text("""
        UPDATE partners 
        SET type = 'DISTRIBUTEUR'::partner_type 
        WHERE type::text = 'FOURNISSEUR';
    """))


def downgrade() -> None:
    """Downgrade schema: Remove DISTRIBUTEUR from partner_type enum."""
    # Note: PostgreSQL doesn't support removing enum values directly.
    # This would require recreating the enum type, which is complex.
    # For now, we'll leave a comment indicating manual intervention is needed.
    # In practice, you would need to:
    # 1. Create a new enum without DISTRIBUTEUR
    # 2. Update all columns using the old enum to the new one
    # 3. Drop the old enum
    # 4. Rename the new enum to the original name
    pass
