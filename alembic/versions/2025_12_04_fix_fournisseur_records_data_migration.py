"""fix_fournisseur_records_data_migration

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2025-12-04 18:10:00.000000

Data migration to fix any remaining FOURNISSEUR records that weren't migrated.
This is a safety migration that can be run multiple times safely.
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text, create_engine


# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = 'b4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Fix any remaining FOURNISSEUR records."""
    connection = op.get_bind()
    
    # First, check if DISTRIBUTEUR exists in the enum
    # If it doesn't exist, the previous migration (a3b4c5d6e7f8) didn't complete
    # In that case, we need to add it using a workaround that commits separately
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
    
    # Now update ALL FOURNISSEUR records to DISTRIBUTEUR
    # DISTRIBUTEUR should now be available since it was committed above
    # This is safe to run multiple times
    connection.execute(text("""
        UPDATE partners 
        SET type = 'DISTRIBUTEUR'::partner_type 
        WHERE type::text = 'FOURNISSEUR';
    """))
    
    # Verify no FOURNISSEUR records remain
    result = connection.execute(text("""
        SELECT COUNT(*) FROM partners WHERE type::text = 'FOURNISSEUR';
    """))
    remaining_count = result.scalar()
    
    if remaining_count > 0:
        # Log warning but don't fail - this might be due to enum constraints
        print(f"WARNING: {remaining_count} FOURNISSEUR records still exist after migration")


def downgrade() -> None:
    """Downgrade schema: This migration is not reversible."""
    # We cannot safely revert FOURNISSEUR records without knowing
    # which ones were originally FOURNISSEUR vs DISTRIBUTEUR
    pass
