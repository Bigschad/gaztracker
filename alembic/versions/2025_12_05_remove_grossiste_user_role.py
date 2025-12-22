"""remove_grossiste_user_role

Revision ID: e7f8a9b0c1d2
Revises: d6e7f8a9b0c1
Create Date: 2025-12-05 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f8a9b0c1d2'
down_revision = 'd6e7f8a9b0c1'
branch_labels = None
depends_on = None


def upgrade():
    """Remove GROSSISTE from user_role enum."""
    
    # First, update any existing users with GROSSISTE role to OPERATEUR_USINE
    # This is a safety measure in case there are any users with this role
    op.execute("""
        UPDATE users 
        SET role = 'OPERATEUR_USINE'::user_role 
        WHERE role::text = 'GROSSISTE';
    """)
    
    # PostgreSQL requires a multi-step process to remove an enum value:
    # 1. Create a new enum type without GROSSISTE
    op.execute("""
        CREATE TYPE user_role_new AS ENUM (
            'ADMIN',
            'RESPONSABLE_LOGISTIQUE',
            'OPERATEUR_USINE',
            'CHAUFFEUR'
        );
    """)
    
    # 2. Alter the column to use the new type
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE user_role_new 
        USING role::text::user_role_new;
    """)
    
    # 3. Drop the old enum type
    op.execute("DROP TYPE user_role;")
    
    # 4. Rename the new type to the original name
    op.execute("ALTER TYPE user_role_new RENAME TO user_role;")


def downgrade():
    """Add GROSSISTE back to user_role enum."""
    
    # Create a new enum type with GROSSISTE
    op.execute("""
        CREATE TYPE user_role_new AS ENUM (
            'ADMIN',
            'RESPONSABLE_LOGISTIQUE',
            'OPERATEUR_USINE',
            'CHAUFFEUR',
            'GROSSISTE'
        );
    """)
    
    # Alter the column to use the new type
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE user_role_new 
        USING role::text::user_role_new;
    """)
    
    # Drop the old enum type
    op.execute("DROP TYPE user_role;")
    
    # Rename the new type to the original name
    op.execute("ALTER TYPE user_role_new RENAME TO user_role;")

