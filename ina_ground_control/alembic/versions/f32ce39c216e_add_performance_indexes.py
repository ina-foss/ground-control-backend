"""add_performance_indexes

Revision ID: f32ce39c216e
Revises: 81eaf5cc7d13
Create Date: 2025-12-19 17:01:26.647959

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f32ce39c216e'
down_revision: Union[str, None] = '81eaf5cc7d13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Index for joins
    op.create_index('idx_step_project_id', 'step', ['project_id'], unique=False)
    op.create_index('idx_task_step_id', 'task', ['step_id'], unique=False)
    op.create_index('idx_annotation_task_id', 'annotation_task', ['task_id'], unique=False)

    # Index for filters
    op.create_index('idx_task_status', 'task', ['status'], unique=False)
    op.create_index('idx_annotation_status', 'annotation', ['annotation_status'], unique=False)
    op.create_index('idx_annotation_user_email', 'annotation', ['user_email'], unique=False)

    # Partial index for task expiration date
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_task_expiration_date
        ON task(expiration_date)
        WHERE expiration_date IS NOT NULL
    """)


def downgrade() -> None:
    # Drop indexes in reverse order
    op.execute('DROP INDEX IF EXISTS idx_task_expiration_date')
    op.drop_index('idx_annotation_user_email', table_name='annotation')
    op.drop_index('idx_annotation_status', table_name='annotation')
    op.drop_index('idx_task_status', table_name='task')
    op.drop_index('idx_annotation_task_id', table_name='annotation_task')
    op.drop_index('idx_task_step_id', table_name='task')
    op.drop_index('idx_step_project_id', table_name='step')
