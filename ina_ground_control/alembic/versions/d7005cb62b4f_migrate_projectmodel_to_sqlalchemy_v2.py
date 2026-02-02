"""Migrate ProjectModel to SQLAlchemy v2

Revision ID: d7005cb62b4f
Revises: 271da1758f48
Create Date: 2026-01-14 14:25:10.588298

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd7005cb62b4f'
down_revision: Union[str, None] = '271da1758f48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new ENUM type (check first to avoid conflict)
    new_status_enum = sa.Enum(
        'DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED', name='status'
    )
    new_status_enum.create(op.get_bind(), checkfirst=True)  # Avoid duplicate creation errors

    # Alter the `status` column: first cast to TEXT, then to the new ENUM
    op.execute("ALTER TABLE project ALTER COLUMN status TYPE TEXT")
    op.alter_column(
        'project',
        'status',
        existing_type=sa.TEXT(),
        type_=new_status_enum,
        existing_nullable=False,
        postgresql_using="status::TEXT::status",  # Cast from TEXT to the new ENUM type
    )

    # Alter the `archived_status` column: first cast to TEXT, then to the new ENUM
    op.execute("ALTER TABLE project ALTER COLUMN archived_status TYPE TEXT")
    op.alter_column(
        'project',
        'archived_status',
        existing_type=sa.TEXT(),
        type_=new_status_enum,
        existing_nullable=True,
        postgresql_using="archived_status::TEXT::status",  # Cast from TEXT to the new ENUM type
    )

    # Fix `created_at` column nullability and default value
    op.alter_column(
        'project',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Drop the old ENUM type (check if it exists before dropping)
    op.execute("DROP TYPE IF EXISTS projectstatus")


def downgrade() -> None:
    # Recreate the old ENUM type (check first to avoid conflict)
    old_status_enum = postgresql.ENUM(
        'DRAFT', 'PENDING', 'IN_PROGRESS', 'SKIPPED', 'DONE', 'ARCHIVED', name='projectstatus'
    )
    old_status_enum.create(op.get_bind(), checkfirst=True)  # Avoid duplicate creation errors

    # Revert the `status` column back to the old ENUM
    op.execute("ALTER TABLE project ALTER COLUMN status TYPE TEXT")
    op.alter_column(
        'project',
        'status',
        existing_type=sa.TEXT(),
        type_=old_status_enum,
        existing_nullable=False,
        postgresql_using="status::TEXT::projectstatus",  # Cast from TEXT to the old ENUM type
    )

    # Revert the `archived_status` column back to the old ENUM
    op.execute("ALTER TABLE project ALTER COLUMN archived_status TYPE TEXT")
    op.alter_column(
        'project',
        'archived_status',
        existing_type=sa.TEXT(),
        type_=old_status_enum,
        existing_nullable=True,
        postgresql_using="archived_status::TEXT::projectstatus",  # Cast from TEXT to the old ENUM type
    )

    # Fix `created_at` column nullability and default value
    op.alter_column(
        'project',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Drop the new ENUM type (check if it exists before dropping)
    op.execute("DROP TYPE IF EXISTS status")
