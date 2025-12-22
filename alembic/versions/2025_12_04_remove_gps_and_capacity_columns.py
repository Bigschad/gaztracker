"""remove_gps_and_capacity_columns

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2025-12-04 20:00:00.000000

Remove GPS coordinates (latitude, longitude) and capacity columns (capacity_b28, capacity_b12, capacity_b6) from depots table.
Remove GPS coordinates from centres_remplisseurs table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e7f8a9b0c1'
down_revision: Union[str, Sequence[str], None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove GPS and capacity columns from depots and centres_remplisseurs."""
    # Drop indexes first
    op.drop_index('ix_depots_location', table_name='depots')
    op.drop_index('ix_centres_location', table_name='centres_remplisseurs')
    
    # Drop columns from depots table
    op.drop_column('depots', 'latitude')
    op.drop_column('depots', 'longitude')
    op.drop_column('depots', 'capacity_b28')
    op.drop_column('depots', 'capacity_b12')
    op.drop_column('depots', 'capacity_b6')
    
    # Drop GPS and capacity columns from centres_remplisseurs table
    op.drop_column('centres_remplisseurs', 'latitude')
    op.drop_column('centres_remplisseurs', 'longitude')
    op.drop_column('centres_remplisseurs', 'capacity_b28')
    op.drop_column('centres_remplisseurs', 'capacity_b12')
    op.drop_column('centres_remplisseurs', 'capacity_b6')


def downgrade() -> None:
    """Re-add GPS and capacity columns to depots and centres_remplisseurs."""
    # Re-add columns to depots table
    op.add_column('depots', sa.Column('latitude', sa.Float(), nullable=True, comment='GPS latitude'))
    op.add_column('depots', sa.Column('longitude', sa.Float(), nullable=True, comment='GPS longitude'))
    op.add_column('depots', sa.Column('capacity_b28', sa.Integer(), nullable=True, comment='Capacity for B28 palettes'))
    op.add_column('depots', sa.Column('capacity_b12', sa.Integer(), nullable=True, comment='Capacity for B12 palettes'))
    op.add_column('depots', sa.Column('capacity_b6', sa.Integer(), nullable=True, comment='Capacity for B6 palettes'))
    
    # Re-add GPS and capacity columns to centres_remplisseurs table
    op.add_column('centres_remplisseurs', sa.Column('latitude', sa.Float(), nullable=True, comment='GPS latitude'))
    op.add_column('centres_remplisseurs', sa.Column('longitude', sa.Float(), nullable=True, comment='GPS longitude'))
    op.add_column('centres_remplisseurs', sa.Column('capacity_b28', sa.Integer(), nullable=True, comment='Capacity for B28 palettes'))
    op.add_column('centres_remplisseurs', sa.Column('capacity_b12', sa.Integer(), nullable=True, comment='Capacity for B12 palettes'))
    op.add_column('centres_remplisseurs', sa.Column('capacity_b6', sa.Integer(), nullable=True, comment='Capacity for B6 palettes'))
    
    # Re-add indexes
    op.create_index('ix_depots_location', 'depots', ['latitude', 'longitude'])
    op.create_index('ix_centres_location', 'centres_remplisseurs', ['latitude', 'longitude'])
