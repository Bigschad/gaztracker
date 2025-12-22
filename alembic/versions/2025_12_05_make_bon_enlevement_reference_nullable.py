"""make_bon_enlevement_reference_nullable

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2025-12-05 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f8a9b0c1d2e3'
down_revision = 'e7f8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade():
    """Make reference column nullable in bons_enlevement table."""
    
    # Alter the reference column to allow NULL values
    op.alter_column(
        'bons_enlevement',
        'reference',
        existing_type=sa.String(length=100),
        nullable=True,
        existing_nullable=False
    )


def downgrade():
    """Revert reference column to NOT NULL."""
    
    # First, set NULL values to empty string or a default value
    op.execute("""
        UPDATE bons_enlevement 
        SET reference = '' 
        WHERE reference IS NULL;
    """)
    
    # Then make the column NOT NULL again
    op.alter_column(
        'bons_enlevement',
        'reference',
        existing_type=sa.String(length=100),
        nullable=False,
        existing_nullable=True
    )
