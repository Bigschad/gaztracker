"""merge heads

Revision ID: merge_heads_2025_11_26
Revises: f6a7b8c9d0e1, phase1_hierarchy
Create Date: 2025-11-26 12:00:00.000000

"""
from typing import Sequence, Union, List

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_heads_2025_11_26'
down_revision: Union[str, Sequence[str], None] = ['f6a7b8c9d0e1', 'phase1_hierarchy']
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration - no schema changes needed
    pass


def downgrade() -> None:
    # This is a merge migration - no schema changes needed
    pass

