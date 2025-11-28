"""create_partner_contact_tables_and_update_expedition

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-10 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create partner_type enum (check if it exists first)
    from sqlalchemy.sql import text
    
    # Check if enum type already exists and create if not
    op.execute(text("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'partner_type') THEN
                CREATE TYPE partner_type AS ENUM ('GROSSISTE', 'FOURNISSEUR', 'TRANSPORTEUR', 'AUTRE');
            END IF;
        END $$;
    """))
    
    # Create partners table using raw SQL to avoid SQLAlchemy's enum creation event
    op.execute(text("""
        CREATE TABLE partners (
            id UUID PRIMARY KEY NOT NULL,
            name VARCHAR(255) NOT NULL,
            type partner_type NOT NULL DEFAULT 'GROSSISTE',
            address VARCHAR(500),
            city VARCHAR(100),
            postal_code VARCHAR(20),
            country VARCHAR(100) DEFAULT 'France',
            phone VARCHAR(20),
            email VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT true,
            notes VARCHAR(1000),
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
    """))
    
    # Create indexes for partners
    op.create_index('ix_partners_name', 'partners', ['name'])
    op.create_index('ix_partners_name_active', 'partners', ['name', 'is_active'])
    op.create_index('ix_partners_type_active', 'partners', ['type', 'is_active'])
    op.create_index('ix_partners_phone', 'partners', ['phone'])
    op.create_index('ix_partners_email', 'partners', ['email'])
    
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('partner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create foreign key for contacts.partner_id
    op.create_foreign_key(
        'fk_contacts_partner_id_partners',
        'contacts', 'partners',
        ['partner_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Create indexes for contacts
    op.create_index('ix_contacts_partner_id', 'contacts', ['partner_id'])
    op.create_index('ix_contacts_name', 'contacts', ['first_name', 'last_name'])
    op.create_index('ix_contacts_phone', 'contacts', ['phone'])
    op.create_index('ix_contacts_email', 'contacts', ['email'])
    op.create_index('ix_contacts_is_primary', 'contacts', ['is_primary'])
    
    # Drop old foreign key constraint for expeditions.grossiste_id (if it exists)
    # First check if the constraint exists
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_expeditions_grossiste_id_users'
            ) THEN
                ALTER TABLE expeditions DROP CONSTRAINT fk_expeditions_grossiste_id_users;
            END IF;
        END $$;
    """)
    
    # Drop old index for expeditions.grossiste_id (if it exists)
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE indexname = 'ix_expeditions_grossiste_id'
            ) THEN
                DROP INDEX ix_expeditions_grossiste_id;
            END IF;
        END $$;
    """)
    
    # Add contact_id column to expeditions
    op.add_column('expeditions',
        sa.Column('contact_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Modify grossiste_id to point to partners instead of users
    # We need to drop and recreate the column because we're changing the FK
    op.execute("""
        ALTER TABLE expeditions 
        DROP CONSTRAINT IF EXISTS expeditions_grossiste_id_fkey;
    """)
    
    # Create new foreign key constraint pointing to partners
    op.create_foreign_key(
        'fk_expeditions_grossiste_id_partners',
        'expeditions', 'partners',
        ['grossiste_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create foreign key constraint for contact_id
    op.create_foreign_key(
        'fk_expeditions_contact_id_contacts',
        'expeditions', 'contacts',
        ['contact_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create indexes
    op.create_index('ix_expeditions_grossiste_id', 'expeditions', ['grossiste_id'])
    op.create_index('ix_expeditions_contact_id', 'expeditions', ['contact_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_expeditions_contact_id', table_name='expeditions')
    op.drop_index('ix_expeditions_grossiste_id', table_name='expeditions')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_expeditions_contact_id_contacts', 'expeditions', type_='foreignkey')
    op.drop_constraint('fk_expeditions_grossiste_id_partners', 'expeditions', type_='foreignkey')
    
    # Drop contact_id column
    op.drop_column('expeditions', 'contact_id')
    
    # Recreate grossiste_id FK to users (if needed)
    # Note: This might fail if there are existing values pointing to partners
    # In a real scenario, you'd need to migrate data first
    
    # Drop contacts table
    op.drop_index('ix_contacts_is_primary', table_name='contacts')
    op.drop_index('ix_contacts_email', table_name='contacts')
    op.drop_index('ix_contacts_phone', table_name='contacts')
    op.drop_index('ix_contacts_name', table_name='contacts')
    op.drop_index('ix_contacts_partner_id', table_name='contacts')
    op.drop_constraint('fk_contacts_partner_id_partners', 'contacts', type_='foreignkey')
    op.drop_table('contacts')
    
    # Drop partners table
    op.drop_index('ix_partners_email', table_name='partners')
    op.drop_index('ix_partners_phone', table_name='partners')
    op.drop_index('ix_partners_type_active', table_name='partners')
    op.drop_index('ix_partners_name_active', table_name='partners')
    op.drop_index('ix_partners_name', table_name='partners')
    op.drop_table('partners')
    
    # Drop partner_type enum
    op.execute('DROP TYPE IF EXISTS partner_type')

