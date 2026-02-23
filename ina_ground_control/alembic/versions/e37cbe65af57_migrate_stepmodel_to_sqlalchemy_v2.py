"""Migrate StepModel to SQLAlchemy v2

Revision ID: e37cbe65af57
Revises: d7005cb62b4f
Create Date: 2026-01-14 15:16:59.150530

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e37cbe65af57'
down_revision: Union[str, None] = 'd7005cb62b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Create the new ENUM type only if it doesn't exist ###
    bind = op.get_bind()
    new_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED', name='status')
    old_enum = postgresql.ENUM('DRAFT', 'PENDING', 'IN_PROGRESS', 'SKIPPED', 'DONE', 'ARCHIVED', name='stepstatus')

    # Create the new ENUM type if it does not already exist
    new_enum.create(bind, checkfirst=True)

    # ### Add a temporary column for the new ENUM ###
    op.add_column('step', sa.Column('status_new', new_enum, nullable=False, server_default='DRAFT'))
    op.add_column('step', sa.Column('archived_status_new', new_enum, nullable=True))

    # ### Copy data to the new columns ###
    op.execute('UPDATE step SET status_new = status::text::status')
    op.execute('UPDATE step SET archived_status_new = archived_status::text::status')

    # ### Drop old columns ###
    op.drop_column('step', 'status')
    op.drop_column('step', 'archived_status')

    # ### Rename the new columns ###
    op.alter_column('step', 'status_new', new_column_name='status')
    op.alter_column('step', 'archived_status_new', new_column_name='archived_status')

    # ### Drop the old ENUM type only if it exists ###
    old_enum.drop(bind, checkfirst=True)


def downgrade() -> None:
    # ### Create the old ENUM type if it doesn't already exist ###
    bind = op.get_bind()
    old_enum = postgresql.ENUM('DRAFT', 'PENDING', 'IN_PROGRESS', 'SKIPPED', 'DONE', 'ARCHIVED', name='stepstatus')
    new_enum = sa.Enum('DRAFT', 'IN_PROGRESS', 'PENDING', 'SKIPPED', 'DONE', 'ARCHIVED', name='status')

    # Create the old ENUM type if needed
    old_enum.create(bind, checkfirst=True)

    # ### Add temporary columns for the old ENUM type ###
    op.add_column('step', sa.Column('status_old', old_enum, nullable=False, server_default='DRAFT'))
    op.add_column('step', sa.Column('archived_status_old', old_enum, nullable=True))

    # ### Copy data back to the old columns ###
    op.execute('UPDATE step SET status_old = status::text::stepstatus')
    op.execute('UPDATE step SET archived_status_old = archived_status::text::stepstatus')

    # ### Drop new columns ###
    op.drop_column('step', 'status')
    op.drop_column('step', 'archived_status')

    # ### Rename old columns back ###
    op.alter_column('step', 'status_old', new_column_name='status')
    op.alter_column('step', 'archived_status_old', new_column_name='archived_status')

    # ### Drop the new ENUM type only if it exists ###
    new_enum.drop(bind, checkfirst=True)
