"""add_palette_condition

Revision ID: i1d2e3f4g5h6
Revises: h0c1d2e3f4g5
Create Date: 2025-12-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i1d2e3f4g5h6'
down_revision = 'h0c1d2e3f4g5'
branch_labels = None
depends_on = None


def upgrade():
    """Add condition column to palettes table."""
    
    # Create the enum type
    palette_condition_enum = postgresql.ENUM('NEUVE', 'RECONDITIONNEE', name='palette_condition', create_type=True)
    palette_condition_enum.create(op.get_bind(), checkfirst=True)
    
    # Add the column with default value
    # Use sa.text() with explicit cast for enum default value (PostgreSQL requirement)
    op.add_column(
        'palettes',
        sa.Column(
            'condition',
            palette_condition_enum,
            nullable=True,
            server_default=sa.text("'NEUVE'::palette_condition"),
            comment='Condition de la palette (NEUVE ou RECONDITIONNEE)'
        )
    )
    
    # Create index for better query performance
    op.create_index(
        'ix_palettes_condition',
        'palettes',
        ['condition']
    )


def downgrade():
    """Remove condition column from palettes table."""
    
    # Drop index first
    op.drop_index('ix_palettes_condition', table_name='palettes')
    
    # Drop column
    op.drop_column('palettes', 'condition')
    
    # Drop the enum type
    palette_condition_enum = postgresql.ENUM('NEUVE', 'RECONDITIONNEE', name='palette_condition', create_type=False)
    palette_condition_enum.drop(op.get_bind(), checkfirst=True)
