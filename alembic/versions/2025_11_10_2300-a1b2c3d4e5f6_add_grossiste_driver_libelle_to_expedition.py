"""add_grossiste_driver_libelle_to_expedition

Revision ID: a1b2c3d4e5f6
Revises: 0bc59d007fbc
Create Date: 2025-11-10 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0bc59d007fbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add grossiste_id column
    op.add_column('expeditions',
        sa.Column('grossiste_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Add driver_id column
    op.add_column('expeditions',
        sa.Column('driver_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Add libelle column
    op.add_column('expeditions',
        sa.Column('libelle', sa.String(length=255), nullable=True)
    )
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_expeditions_grossiste_id_users',
        'expeditions', 'users',
        ['grossiste_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_expeditions_driver_id_users',
        'expeditions', 'users',
        ['driver_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create indexes
    op.create_index('ix_expeditions_grossiste_id', 'expeditions', ['grossiste_id'])
    op.create_index('ix_expeditions_driver_id', 'expeditions', ['driver_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_expeditions_driver_id', table_name='expeditions')
    op.drop_index('ix_expeditions_grossiste_id', table_name='expeditions')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_expeditions_driver_id_users', 'expeditions', type_='foreignkey')
    op.drop_constraint('fk_expeditions_grossiste_id_users', 'expeditions', type_='foreignkey')
    
    # Drop columns
    op.drop_column('expeditions', 'libelle')
    op.drop_column('expeditions', 'driver_id')
    op.drop_column('expeditions', 'grossiste_id')

