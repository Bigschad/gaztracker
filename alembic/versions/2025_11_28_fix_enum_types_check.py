"""fix enum types check

Revision ID: fix_enum_types_check
Revises: add_logo_to_groupe
Create Date: 2025-11-28 09:15:00.000000

This migration fixes the issue where ENUM types are created without checking if they already exist.
It ensures that all ENUM types are created safely with checkfirst=True.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_enum_types_check'
down_revision: Union[str, None] = 'add_logo_to_groupe'  # Will be updated if add_missing_tables exists
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure all ENUM types exist, creating them only if they don't."""
    conn = op.get_bind()
    
    # Helper function to create ENUM if it doesn't exist
    def create_enum_if_not_exists(enum_name: str, enum_values: list):
        result = conn.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
        ), {"name": enum_name})
        exists = result.scalar()
        if not exists:
            enum = postgresql.ENUM(*enum_values, name=enum_name)
            enum.create(conn, checkfirst=True)
    
    # Ensure all ENUM types exist
    create_enum_if_not_exists('palette_type', ['B6', 'B12', 'B28'])
    create_enum_if_not_exists('bon_enlevement_status', 
        ['CREATION', 'VALIDE', 'EN_CHARGEMENT', 'EN_ROUTE', 'EN_LIVRAISON', 'TERMINE', 'ANNULE'])
    create_enum_if_not_exists('livraison_status',
        ['EN_ATTENTE', 'EN_COURS', 'LIVREE', 'PROBLEME', 'ANNULEE'])
    create_enum_if_not_exists('bon_reception_retour_status',
        ['CREATION', 'EN_ROUTE', 'ARRIVE', 'EN_CONTROLE', 'VALIDE', 'REFUSE'])
    create_enum_if_not_exists('detail_retour_type',
        ['PALETTE_VIDE', 'BOUTEILLE_VIDE', 'CONSIGNE'])
    create_enum_if_not_exists('detail_retour_etat',
        ['BON', 'MOYEN', 'MAUVAIS', 'REFUSE'])


def downgrade() -> None:
    """No downgrade needed - this is just a safety check migration."""
    pass

