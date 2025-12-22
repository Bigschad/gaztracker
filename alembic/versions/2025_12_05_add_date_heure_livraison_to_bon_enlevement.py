"""add_date_heure_livraison_to_bon_enlevement

Revision ID: g9b0c1d2e3f4
Revises: f8a9b0c1d2e3
Create Date: 2025-12-05 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'g9b0c1d2e3f4'
down_revision = 'f8a9b0c1d2e3'
branch_labels = None
depends_on = None


def upgrade():
    """Add date_heure_livraison column to bons_enlevement table."""
    
    op.add_column(
        'bons_enlevement',
        sa.Column(
            'date_heure_livraison',
            sa.DateTime(),
            nullable=True,
            comment='Scheduled delivery date and time'
        )
    )
    
    # Create index for better query performance
    op.create_index(
        'ix_bons_enlevement_date_heure_livraison',
        'bons_enlevement',
        ['date_heure_livraison']
    )


def downgrade():
    """Remove date_heure_livraison column from bons_enlevement table."""
    
    # Drop index first
    op.drop_index('ix_bons_enlevement_date_heure_livraison', table_name='bons_enlevement')
    
    # Drop column
    op.drop_column('bons_enlevement', 'date_heure_livraison')
