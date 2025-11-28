"""add fields to palette

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2025-11-12 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    # Add reference_code column
    op.add_column('palettes', sa.Column('reference_code', sa.String(length=50), nullable=True))
    op.create_index('ix_palettes_reference_code', 'palettes', ['reference_code'])
    op.create_unique_constraint('uq_palettes_reference_code', 'palettes', ['reference_code'])
    
    # Add capacity column
    op.add_column('palettes', sa.Column('capacity', sa.Integer(), nullable=True))
    
    # Add manufacturing_date column
    op.add_column('palettes', sa.Column('manufacturing_date', sa.Date(), nullable=True))
    
    # Add current_partner_id column
    op.add_column('palettes', sa.Column('current_partner_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_palettes_current_partner_id_partners', 'palettes', 'partners', ['current_partner_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_palettes_current_partner_id', 'palettes', ['current_partner_id'])


def downgrade():
    # Drop current_partner_id
    op.drop_index('ix_palettes_current_partner_id', table_name='palettes')
    op.drop_constraint('fk_palettes_current_partner_id_partners', 'palettes', type_='foreignkey')
    op.drop_column('palettes', 'current_partner_id')
    
    # Drop manufacturing_date
    op.drop_column('palettes', 'manufacturing_date')
    
    # Drop capacity
    op.drop_column('palettes', 'capacity')
    
    # Drop reference_code
    op.drop_constraint('uq_palettes_reference_code', 'palettes', type_='unique')
    op.drop_index('ix_palettes_reference_code', table_name='palettes')
    op.drop_column('palettes', 'reference_code')

