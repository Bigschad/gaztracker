"""add_groupe_id_to_partners

Revision ID: h0c1d2e3f4g5
Revises: g9b0c1d2e3f4
Create Date: 2025-12-05 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h0c1d2e3f4g5'
down_revision = 'g9b0c1d2e3f4'
branch_labels = None
depends_on = None


def upgrade():
    """Add groupe_id column to partners table."""
    
    op.add_column(
        'partners',
        sa.Column(
            'groupe_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='FK to groupe (for DISTRIBUTEUR only)'
        )
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_partners_groupe_id',
        'partners',
        'groupes',
        ['groupe_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for better query performance
    op.create_index(
        'ix_partners_groupe_id',
        'partners',
        ['groupe_id']
    )


def downgrade():
    """Remove groupe_id column from partners table."""
    
    # Drop index first
    op.drop_index('ix_partners_groupe_id', table_name='partners')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_partners_groupe_id', 'partners', type_='foreignkey')
    
    # Drop column
    op.drop_column('partners', 'groupe_id')
