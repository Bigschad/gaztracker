"""add_serial_number_to_palette

Revision ID: 0bc59d007fbc
Revises: 1a8dff9c71d0
Create Date: 2025-11-08 02:22:03.201693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bc59d007fbc'
down_revision: Union[str, Sequence[str], None] = '1a8dff9c71d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add the serial_number column as nullable first
    op.add_column('palettes',
        sa.Column('serial_number', sa.String(length=20), nullable=True)
    )

    # Step 2: Populate serial_number for existing palettes
    # This uses a SQL query to generate sequential numbers
    from sqlalchemy.sql import text
    connection = op.get_bind()

    # Get all palettes and assign serial numbers
    result = connection.execute(text("SELECT id, created_at FROM palettes ORDER BY created_at"))
    palettes = result.fetchall()

    from datetime import datetime
    year = datetime.now().year
    for idx, palette in enumerate(palettes, start=1):
        serial_number = f"PAL-{year}-{idx:05d}"
        connection.execute(
            text("UPDATE palettes SET serial_number = :serial WHERE id = :id"),
            {"serial": serial_number, "id": str(palette[0])}
        )

    # Step 3: Make the column NOT NULL and UNIQUE
    op.alter_column('palettes', 'serial_number',
                    existing_type=sa.String(length=20),
                    nullable=False)

    op.create_unique_constraint('uq_palettes_serial_number', 'palettes', ['serial_number'])
    op.create_index('ix_palettes_serial_number', 'palettes', ['serial_number'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_palettes_serial_number', table_name='palettes')
    op.drop_constraint('uq_palettes_serial_number', 'palettes', type_='unique')
    op.drop_column('palettes', 'serial_number')
