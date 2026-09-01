"""add indexes for task.step_id and annotation_task.task_id

Revision ID: 1dbffb426a9b
Revises: b3bc57fab2ab
Create Date: 2026-08-04 00:00:00.000000

These join columns are heavily used (listing a step's tasks, joining
annotations to tasks). The same index names as ``f32ce39c216e`` are reused with
``IF NOT EXISTS`` guards, so this stays idempotent and does not create duplicate
indexes when the migration heads are eventually merged.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1dbffb426a9b"
down_revision: Union[str, None] = "b3bc57fab2ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS idx_task_step_id ON task (step_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_annotation_task_id "
        "ON annotation_task (task_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_annotation_task_id")
    op.execute("DROP INDEX IF EXISTS idx_task_step_id")
