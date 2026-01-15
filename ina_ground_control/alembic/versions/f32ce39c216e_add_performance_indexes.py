"""
add_performance_indexes

Revision ID: f32ce39c216e
Revises: 81eaf5cc7d13
Create Date: 2025-12-19 17:01:26.647959
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f32ce39c216e"
down_revision: Union[str, None] = "81eaf5cc7d13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Indexes for joins
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_step_project_id'
        ) THEN
            CREATE INDEX idx_step_project_id ON step (project_id);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_task_step_id'
        ) THEN
            CREATE INDEX idx_task_step_id ON task (step_id);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_annotation_task_id'
        ) THEN
            CREATE INDEX idx_annotation_task_id ON annotation_task (task_id);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_task_status'
        ) THEN
            CREATE INDEX idx_task_status ON task (status);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_annotation_status'
        ) THEN
            CREATE INDEX idx_annotation_status ON annotation (annotation_status);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE indexname = 'idx_annotation_user_email'
        ) THEN
            CREATE INDEX idx_annotation_user_email ON annotation (user_email);
        END IF;
    END $$;
    """)

    # Partial index (Postgres supports IF NOT EXISTS directly)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_task_expiration_date
        ON task (expiration_date)
        WHERE expiration_date IS NOT NULL
    """)


def downgrade() -> None:
    # Drop indexes safely
    op.execute("""
        DROP INDEX IF EXISTS idx_task_expiration_date;
        DROP INDEX IF EXISTS idx_annotation_user_email;
        DROP INDEX IF EXISTS idx_annotation_status;
        DROP INDEX IF EXISTS idx_task_status;
        DROP INDEX IF EXISTS idx_annotation_task_id;
        DROP INDEX IF EXISTS idx_task_step_id;
        DROP INDEX IF EXISTS idx_step_project_id;
    """)
