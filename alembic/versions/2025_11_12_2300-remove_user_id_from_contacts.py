"""remove user_id from contacts

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2025-11-12 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_contacts_user_id_users', 'contacts', type_='foreignkey')
    
    # Drop unique constraint
    op.drop_constraint('uq_contacts_user_id', 'contacts', type_='unique')
    
    # Drop index
    op.drop_index('ix_contacts_user_id', table_name='contacts')
    
    # Drop column
    op.drop_column('contacts', 'user_id')


def downgrade():
    # Add column back
    from sqlalchemy.dialects.postgresql import UUID
    op.add_column('contacts', sa.Column('user_id', UUID(as_uuid=True), nullable=True))
    
    # Recreate index
    op.create_index('ix_contacts_user_id', 'contacts', ['user_id'])
    
    # Recreate unique constraint
    op.create_unique_constraint('uq_contacts_user_id', 'contacts', ['user_id'])
    
    # Recreate foreign key
    op.create_foreign_key('fk_contacts_user_id_users', 'contacts', 'users', ['user_id'], ['id'], ondelete='SET NULL')

