"""add_indexes

Revision ID: f0e75c5f346e
Revises: e37cbe65af57
Create Date: 2026-01-30 17:42:52.665847

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f0e75c5f346e'
down_revision: Union[str, None] = 'e37cbe65af57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index('idx_step_project_id', 'step', ['project_id'])
    op.create_index('idx_task_step_id', 'task', ['step_id'])
    op.create_index('idx_task_status', 'task', ['status'])
    op.create_index('idx_annotation_user_email', 'annotation', ['user_email'])
    op.create_index('idx_annotation_status', 'annotation', ['annotation_status'])
    # Index composite pour les requetes frequentes
    op.create_index(
        'idx_annotation_user_status',
        'annotation',
        ['user_email', 'annotation_status']
    )

def downgrade():
    op.drop_index('idx_step_project_id', 'step')
    op.drop_index('idx_task_step_id', 'task')
    op.drop_index('idx_task_status', 'task')
    op.drop_index('idx_annotation_user_email', 'annotation')
    op.drop_index('idx_annotation_status', 'annotation')
    op.drop_index('idx_annotation_user_status', 'annotation')
