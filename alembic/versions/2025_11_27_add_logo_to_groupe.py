"""add logo to groupe

Revision ID: add_logo_to_groupe
Revises: 2025_11_26_add_missing_columns
Create Date: 2025-11-27 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_logo_to_groupe'
down_revision = 'add_missing_columns_2025_11_26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add logo_url column to groupes table
    op.add_column('groupes', sa.Column('logo_url', sa.String(500), nullable=True, comment='URL or path to the group logo'))


def downgrade() -> None:
    # Remove logo_url column from groupes table
    op.drop_column('groupes', 'logo_url')

