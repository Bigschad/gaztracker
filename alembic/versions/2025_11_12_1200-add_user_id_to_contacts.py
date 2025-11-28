"""add_user_id_to_contacts

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-11-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add user_id column to contacts table
    op.add_column('contacts',
        sa.Column('user_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_contacts_user_id_users',
        'contacts', 'users',
        ['user_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create unique constraint (one user can only be linked to one contact)
    op.create_unique_constraint(
        'uq_contacts_user_id',
        'contacts',
        ['user_id']
    )
    
    # Create index
    op.create_index('ix_contacts_user_id', 'contacts', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_contacts_user_id', table_name='contacts')
    
    # Drop unique constraint
    op.drop_constraint('uq_contacts_user_id', 'contacts', type_='unique')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_contacts_user_id_users', 'contacts', type_='foreignkey')
    
    # Drop column
    op.drop_column('contacts', 'user_id')

