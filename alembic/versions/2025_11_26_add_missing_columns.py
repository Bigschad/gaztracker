"""add missing columns

Revision ID: add_missing_columns_2025_11_26
Revises: merge_heads_2025_11_26
Create Date: 2025-11-26 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_missing_columns_2025_11_26'
down_revision: Union[str, None] = 'merge_heads_2025_11_26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to groupes table
    op.add_column('groupes', sa.Column('postal_code', sa.String(length=20), nullable=True, comment='Postal code'))
    op.add_column('groupes', sa.Column('country', sa.String(length=100), nullable=True, default="Côte d'Ivoire", comment='Country'))
    
    # Add missing columns to centres_remplisseurs table
    op.add_column('centres_remplisseurs', sa.Column('capacity_b28', sa.Integer(), nullable=True, comment='Capacity for B28 palettes'))
    op.add_column('centres_remplisseurs', sa.Column('capacity_b12', sa.Integer(), nullable=True, comment='Capacity for B12 palettes'))
    op.add_column('centres_remplisseurs', sa.Column('capacity_b6', sa.Integer(), nullable=True, comment='Capacity for B6 palettes'))
    
    # Add missing columns to bons_enlevement table
    op.add_column('bons_enlevement', sa.Column('palette_count', sa.Integer(), nullable=False, server_default='0', comment='Number of palettes'))
    op.add_column('bons_enlevement', sa.Column('livraison_count', sa.Integer(), nullable=False, server_default='0', comment='Number of deliveries'))


def downgrade() -> None:
    # Remove columns from bons_enlevement table
    op.drop_column('bons_enlevement', 'livraison_count')
    op.drop_column('bons_enlevement', 'palette_count')
    
    # Remove columns from centres_remplisseurs table
    op.drop_column('centres_remplisseurs', 'capacity_b6')
    op.drop_column('centres_remplisseurs', 'capacity_b12')
    op.drop_column('centres_remplisseurs', 'capacity_b28')
    
    # Remove columns from groupes table
    op.drop_column('groupes', 'country')
    op.drop_column('groupes', 'postal_code')

