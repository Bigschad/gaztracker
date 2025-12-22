"""add_grand_distributeur_id_to_centres_remplisseurs

Revision ID: f7e8d9c0b1a2
Revises: 3fa8162c308d
Create Date: 2025-12-04 10:45:00.000000

Add grand_distributeur_id column to centres_remplisseurs table.
This allows centres remplisseurs to belong to both a partner (distributeur) and a grand distributeur.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f7e8d9c0b1a2'
down_revision: Union[str, Sequence[str], None] = '3fa8162c308d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add grand_distributeur_id column to centres_remplisseurs."""
    # Add the grand_distributeur_id column (nullable initially to allow existing data)
    op.add_column(
        'centres_remplisseurs',
        sa.Column(
            'grand_distributeur_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='FK to grand_distributeurs'
        )
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'centres_remplisseurs_grand_distributeur_id_fkey',
        'centres_remplisseurs',
        'grand_distributeurs',
        ['grand_distributeur_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create index
    op.create_index(
        'ix_centres_grand_dist',
        'centres_remplisseurs',
        ['grand_distributeur_id', 'is_active'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema: Remove grand_distributeur_id column from centres_remplisseurs."""
    # Drop the index
    op.drop_index('ix_centres_grand_dist', table_name='centres_remplisseurs')
    
    # Drop the foreign key constraint
    op.drop_constraint(
        'centres_remplisseurs_grand_distributeur_id_fkey',
        'centres_remplisseurs',
        type_='foreignkey'
    )
    
    # Drop the column
    op.drop_column('centres_remplisseurs', 'grand_distributeur_id')
