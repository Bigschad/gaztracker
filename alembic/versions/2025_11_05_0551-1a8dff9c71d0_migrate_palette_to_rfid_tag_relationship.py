"""migrate_palette_to_rfid_tag_relationship

Revision ID: 1a8dff9c71d0
Revises: 502160f9945d
Create Date: 2025-11-05 05:51:14.477343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = '1a8dff9c71d0'
down_revision: Union[str, Sequence[str], None] = '502160f9945d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema to separate RFID tags into their own table.

    Changes:
    1. Create rfid_tags table
    2. Migrate existing palette.rfid_tag data to rfid_tags table
    3. Add palette.rfid_tag_id foreign key column
    4. Drop old palette.rfid_tag column
    5. Update indexes
    """

    # Step 1: Create rfid_tags table
    op.create_table(
        'rfid_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tag_number', sa.String(length=50), unique=True, nullable=False, index=True),
        sa.Column('status', sa.Enum('NOT_ASSIGNED', 'ASSIGNED', 'LOST', 'DAMAGED', name='rfidtagstatus'),
                  nullable=False, default='NOT_ASSIGNED', index=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
    )

    # Create indexes on rfid_tags
    op.create_index('ix_rfid_tags_id', 'rfid_tags', ['id'])
    op.create_index('ix_rfid_tags_tag_number', 'rfid_tags', ['tag_number'], unique=True)
    op.create_index('ix_rfid_tags_status', 'rfid_tags', ['status'])
    op.create_index('ix_rfid_tags_created_by_id', 'rfid_tags', ['created_by_id'])
    op.create_index('ix_rfid_tags_created_at', 'rfid_tags', ['created_at'])

    # Step 2: Add new rfid_tag_id column to palettes (nullable initially)
    op.add_column('palettes',
                  sa.Column('rfid_tag_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Step 3: Migrate data
    # For each existing palette:
    # - Create a corresponding RFID tag entry with tag_number from palette.rfid_tag
    # - Set palette.rfid_tag_id to the new RFID tag's ID
    # - Mark tag as ASSIGNED

    # Use raw SQL for data migration
    connection = op.get_bind()

    # Get all existing palettes
    result = connection.execute(sa.text("""
        SELECT id, rfid_tag, created_by_id, created_at
        FROM palettes
        WHERE rfid_tag IS NOT NULL
    """))

    palettes = result.fetchall()

    for palette in palettes:
        palette_id = palette[0]
        tag_number = palette[1]
        created_by_id = palette[2]
        created_at = palette[3]

        # Create RFID tag
        tag_id = uuid.uuid4()
        connection.execute(sa.text("""
            INSERT INTO rfid_tags (id, tag_number, status, created_by_id, notes, is_active, created_at, updated_at, assigned_at)
            VALUES (:tag_id, :tag_number, 'ASSIGNED', :created_by_id, 'Migrated from existing palette', true, :created_at, :created_at, :created_at)
        """), {
            'tag_id': str(tag_id),
            'tag_number': tag_number,
            'created_by_id': str(created_by_id) if created_by_id else None,
            'created_at': created_at
        })

        # Update palette with new rfid_tag_id
        connection.execute(sa.text("""
            UPDATE palettes
            SET rfid_tag_id = :tag_id
            WHERE id = :palette_id
        """), {
            'tag_id': str(tag_id),
            'palette_id': str(palette_id)
        })

    # Step 4: Drop old indexes related to rfid_tag column
    op.drop_index('ix_palettes_rfid_status', table_name='palettes')
    op.drop_index('ix_palettes_rfid_tag', table_name='palettes')

    # Step 5: Drop old rfid_tag column
    op.drop_column('palettes', 'rfid_tag')

    # Step 6: Create new indexes for rfid_tag_id
    op.create_index('ix_palettes_rfid_tag_id', 'palettes', ['rfid_tag_id'], unique=True)
    op.create_index('ix_palettes_rfid_tag_id_status', 'palettes', ['rfid_tag_id', 'status'])

    # Step 7: Add foreign key constraint
    op.create_foreign_key(
        'fk_palettes_rfid_tag_id',
        'palettes', 'rfid_tags',
        ['rfid_tag_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """
    Downgrade schema back to string-based RFID tags.

    This is a lossy operation - some RFID tag metadata will be lost.
    """

    # Step 1: Add back rfid_tag string column
    op.add_column('palettes', sa.Column('rfid_tag', sa.String(length=50), nullable=True))

    # Step 2: Migrate data back
    connection = op.get_bind()

    # Copy tag_number from rfid_tags back to palettes.rfid_tag
    connection.execute(sa.text("""
        UPDATE palettes p
        SET rfid_tag = rt.tag_number
        FROM rfid_tags rt
        WHERE p.rfid_tag_id = rt.id
    """))

    # Step 3: Drop foreign key constraint
    op.drop_constraint('fk_palettes_rfid_tag_id', 'palettes', type_='foreignkey')

    # Step 4: Drop new indexes
    op.drop_index('ix_palettes_rfid_tag_id_status', table_name='palettes')
    op.drop_index('ix_palettes_rfid_tag_id', table_name='palettes')

    # Step 5: Drop rfid_tag_id column
    op.drop_column('palettes', 'rfid_tag_id')

    # Step 6: Recreate old indexes
    op.create_index('ix_palettes_rfid_tag', 'palettes', ['rfid_tag'], unique=True)
    op.create_index('ix_palettes_rfid_status', 'palettes', ['rfid_tag', 'status'])

    # Step 7: Make rfid_tag NOT NULL
    op.alter_column('palettes', 'rfid_tag', nullable=False)

    # Step 8: Drop rfid_tags table and all its data
    op.drop_index('ix_rfid_tags_created_at', table_name='rfid_tags')
    op.drop_index('ix_rfid_tags_created_by_id', table_name='rfid_tags')
    op.drop_index('ix_rfid_tags_status', table_name='rfid_tags')
    op.drop_index('ix_rfid_tags_tag_number', table_name='rfid_tags')
    op.drop_index('ix_rfid_tags_id', table_name='rfid_tags')
    op.drop_table('rfid_tags')

    # Drop enum type
    op.execute('DROP TYPE IF EXISTS rfidtagstatus')
