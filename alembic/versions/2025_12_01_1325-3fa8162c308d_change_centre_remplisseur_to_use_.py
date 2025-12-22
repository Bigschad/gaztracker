"""change_centre_remplisseur_to_use_partner_id

Revision ID: 3fa8162c308d
Revises: 1712b3ff53b4
Create Date: 2025-12-01 13:25:48.588937

Change CentreRemplisseur to use partner_id instead of grand_distributeur_id.
This allows centres remplisseurs to be linked directly to partners (GROSSISTE type).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3fa8162c308d'
down_revision: Union[str, Sequence[str], None] = '1712b3ff53b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Change grand_distributeur_id to partner_id."""
    # First, clean up orphaned records: find centres_remplisseurs with grand_distributeur_id
    # that don't exist in partners table
    # We'll delete these orphaned records to avoid foreign key violations
    op.execute("""
        DELETE FROM centres_remplisseurs
        WHERE grand_distributeur_id NOT IN (
            SELECT id FROM partners
        )
    """)
    
    # Drop the existing index
    op.drop_index('ix_centres_grand_dist', table_name='centres_remplisseurs')
    
    # Drop the foreign key constraint
    op.drop_constraint(
        'centres_remplisseurs_grand_distributeur_id_fkey',
        'centres_remplisseurs',
        type_='foreignkey'
    )
    
    # Rename the column
    op.alter_column(
        'centres_remplisseurs',
        'grand_distributeur_id',
        new_column_name='partner_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        comment='FK to partners (distributeur)'
    )
    
    # Create new foreign key constraint to partners table
    op.create_foreign_key(
        'centres_remplisseurs_partner_id_fkey',
        'centres_remplisseurs',
        'partners',
        ['partner_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create new index
    op.create_index(
        'ix_centres_partner',
        'centres_remplisseurs',
        ['partner_id', 'is_active'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema: Change partner_id back to grand_distributeur_id."""
    # Drop the new index
    op.drop_index('ix_centres_partner', table_name='centres_remplisseurs')
    
    # Drop the foreign key constraint
    op.drop_constraint(
        'centres_remplisseurs_partner_id_fkey',
        'centres_remplisseurs',
        type_='foreignkey'
    )
    
    # Rename the column back
    op.alter_column(
        'centres_remplisseurs',
        'partner_id',
        new_column_name='grand_distributeur_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        comment='FK to grand_distributeurs'
    )
    
    # Create old foreign key constraint
    op.create_foreign_key(
        'centres_remplisseurs_grand_distributeur_id_fkey',
        'centres_remplisseurs',
        'grand_distributeurs',
        ['grand_distributeur_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create old index
    op.create_index(
        'ix_centres_grand_dist',
        'centres_remplisseurs',
        ['grand_distributeur_id', 'is_active'],
        unique=False
    )
