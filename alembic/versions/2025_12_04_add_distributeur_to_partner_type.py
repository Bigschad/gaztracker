"""add_distributeur_to_partner_type

Revision ID: a3b4c5d6e7f8
Revises: f7e8d9c0b1a2
Create Date: 2025-12-04 12:30:00.000000

Add DISTRIBUTEUR value to partner_type enum (replaces FOURNISSEUR).
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text, create_engine


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'f7e8d9c0b1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add DISTRIBUTEUR to partner_type enum and update existing data."""
    # PostgreSQL doesn't allow using a new enum value in the same transaction where it's created.
    # We need to commit the enum addition before using it. We use a separate connection with
    # autocommit to add the enum value, then use the main connection to update data.
    connection = op.get_bind()
    
    # Step 1: Check if DISTRIBUTEUR already exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumlabel = 'DISTRIBUTEUR' 
            AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'partner_type')
        )
    """))
    enum_exists = result.scalar()
    
    if not enum_exists:
        # DISTRIBUTEUR doesn't exist - we need to add it
        # PostgreSQL requires enum values to be committed before use
        # We use a workaround: create a separate connection that autocommits
        from app.config import settings
        
        # Get database URL and create a separate engine with autocommit
        db_url = settings.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )
        temp_engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
        
        with temp_engine.connect() as temp_conn:
            # Add DISTRIBUTEUR enum value in autocommit mode
            # PostgreSQL doesn't support IF NOT EXISTS, so we check first
            check_result = temp_conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'DISTRIBUTEUR' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'partner_type')
                )
            """))
            if not check_result.scalar():
                try:
                    temp_conn.execute(text("ALTER TYPE partner_type ADD VALUE 'DISTRIBUTEUR'"))
                except Exception:
                    # If it fails, the enum might already exist from a concurrent operation
                    pass
        
        temp_engine.dispose()
    
    # Step 2: Now update existing FOURNISSEUR records to DISTRIBUTEUR
    # DISTRIBUTEUR should now be available since it was committed above
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
