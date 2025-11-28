"""add label to rfid_tags

Revision ID: add_label_to_rfid_tags
Revises: add_user_id_to_contacts
Create Date: 2025-11-12 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    # Add label column to rfid_tags table
    op.add_column('rfid_tags', sa.Column('label', sa.String(length=255), nullable=True))
    # Create index on label column
    op.create_index('ix_rfid_tags_label', 'rfid_tags', ['label'])


def downgrade():
    # Drop index
    op.drop_index('ix_rfid_tags_label', table_name='rfid_tags')
    # Drop label column
    op.drop_column('rfid_tags', 'label')

