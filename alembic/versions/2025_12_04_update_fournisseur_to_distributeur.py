"""update_fournisseur_to_distributeur

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2025-12-04 16:30:00.000000

Update existing FOURNISSEUR records to DISTRIBUTEUR in partners table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, Sequence[str], None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Update FOURNISSEUR to DISTRIBUTEUR in existing records."""
    # This migration is now a no-op because the enum addition and data update
    # are both handled in migration a3b4c5d6e7f8 to ensure atomicity.
    # This migration is kept for backward compatibility with existing migration history.
    pass


def downgrade() -> None:
    """Downgrade schema: Revert DISTRIBUTEUR back to FOURNISSEUR."""
    # Note: This assumes FOURNISSEUR still exists in the enum.
    # If FOURNISSEUR was removed, this would fail.
    # In practice, you might want to check if FOURNISSEUR exists first.
    op.execute("""
        UPDATE partners 
        SET type = 'FOURNISSEUR'::partner_type 
        WHERE type = 'DISTRIBUTEUR'::partner_type;
    """)
