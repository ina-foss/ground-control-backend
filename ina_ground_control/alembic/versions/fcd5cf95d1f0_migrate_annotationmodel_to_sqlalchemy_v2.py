"""Migrate AnnotationModel to SQLAlchemy v2

Revision ID: fcd5cf95d1f0
Revises: f32ce39c216e
Create Date: 2026-01-14 10:54:12.541369

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision: str = 'fcd5cf95d1f0'
down_revision: Union[str, None] = 'f32ce39c216e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new ENUM type
    status_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED', name='status')
    status_enum.create(op.get_bind(), checkfirst=True)

    # Add a temporary column with the new ENUM type
    op.add_column('annotation', sa.Column('annotation_status_temp', status_enum, nullable=True))
    op.add_column('annotation', sa.Column('archived_status_temp', status_enum, nullable=True))

    # Migrate data from old ENUM column to the temporary column
    op.execute("""
        UPDATE annotation
        SET
            annotation_status_temp = annotation_status::text::status,
            archived_status_temp = archived_status::text::status
    """)

    # Drop old columns
    op.drop_column('annotation', 'annotation_status')
    op.drop_column('annotation', 'archived_status')

    # Rename temporary columns to the original column names
    op.alter_column('annotation', 'annotation_status_temp', new_column_name='annotation_status')
    op.alter_column('annotation', 'archived_status_temp', new_column_name='archived_status')

    # Ensure constraints or indexes are added where necessary (optional, based on your original config)

    # Drop the old ENUM type
    old_annotationstatus_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED',
                                        name='annotationstatus')
    old_annotationstatus_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Recreate the old ENUM type
    old_annotationstatus_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED',
                                        name='annotationstatus')
    old_annotationstatus_enum.create(op.get_bind(), checkfirst=True)

    # Add a temporary column with the old ENUM type
    op.add_column('annotation', sa.Column('annotation_status_temp', old_annotationstatus_enum, nullable=True))
    op.add_column('annotation', sa.Column('archived_status_temp', old_annotationstatus_enum, nullable=True))

    # Migrate data back to the old ENUM type
    op.execute("""
        UPDATE annotation
        SET 
            annotation_status_temp = annotation_status::text::annotationstatus,
            archived_status_temp = archived_status::text::annotationstatus
    """)

    # Drop new columns
    op.drop_column('annotation', 'annotation_status')
    op.drop_column('annotation', 'archived_status')

    # Rename temporary columns to the original column names
    op.alter_column('annotation', 'annotation_status_temp', new_column_name='annotation_status')
    op.alter_column('annotation', 'archived_status_temp', new_column_name='archived_status')

    # Drop the new ENUM type
    status_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED', name='status')
    status_enum.drop(op.get_bind(), checkfirst=True)
