"""
Rename archived_status to previous_status

Revision ID: 31a101b4ea0b
Revises: f0e75c5f346e
Create Date: 2026-02-09 10:25:44.031735
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "31a101b4ea0b"
down_revision: Union[str, None] = "f0e75c5f346e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # annotation
    # -------------------------------------------------------------------------
    op.add_column(
        "annotation",
        sa.Column(
            "previous_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.drop_index(op.f("idx_annotation_status"), table_name="annotation")
    op.drop_index(op.f("idx_annotation_user_email"), table_name="annotation")
    op.drop_index(op.f("idx_annotation_user_status"), table_name="annotation")
    op.drop_column("annotation", "archived_status")

    # -------------------------------------------------------------------------
    # project
    # -------------------------------------------------------------------------
    op.add_column(
        "project",
        sa.Column(
            "previous_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.alter_column("project", "description", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("project", "is_published", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column(
        "project", "empty_annotations", existing_type=sa.BOOLEAN(), nullable=False
    )
    op.alter_column("project", "allow_skip", existing_type=sa.BOOLEAN(), nullable=False)
    op.drop_column("project", "archived_status")

    # -------------------------------------------------------------------------
    # step
    # -------------------------------------------------------------------------
    op.add_column(
        "step",
        sa.Column(
            "previous_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    # backfill timestamps BEFORE enforcing NOT NULL
    op.execute(
        text(
            """
            UPDATE step
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )
    )
    op.execute(
        text(
            """
            UPDATE step
            SET updated_at = created_at
            WHERE updated_at IS NULL
            """
        )
    )

    op.alter_column(
        "step",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.alter_column(
        "step",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.drop_index(op.f("idx_step_project_id"), table_name="step")
    op.drop_column("step", "archived_status")

    # -------------------------------------------------------------------------
    # tag
    # -------------------------------------------------------------------------
    op.alter_column("tag", "value", existing_type=sa.VARCHAR(), nullable=False)

    # -------------------------------------------------------------------------
    # task
    # -------------------------------------------------------------------------
    op.add_column(
        "task",
        sa.Column(
            "previous_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    # backfill timestamps
    op.execute(
        text(
            """
            UPDATE task
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )
    )
    op.execute(
        text(
            """
            UPDATE task
            SET updated_at = created_at
            WHERE updated_at IS NULL
            """
        )
    )

    # enum migration: taskstatus -> TEXT -> status
    op.alter_column(
        "task",
        "status",
        existing_type=postgresql.ENUM(
            "DRAFT",
            "PENDING",
            "IN_PROGRESS",
            "SKIPPED",
            "DONE",
            "ARCHIVED",
            name="taskstatus",
        ),
        type_=sa.TEXT(),
        postgresql_using="status::text",
    )

    op.alter_column(
        "task",
        "status",
        type_=postgresql.ENUM(
            "DRAFT",
            "IN_PROGRESS",
            "PENDING",
            "SKIPPED",
            "DONE",
            "ARCHIVED",
            name="status",
            create_type=False,
        ),
        postgresql_using="status::status",
        existing_nullable=True,
    )

    op.alter_column(
        "task",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.alter_column(
        "task",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.drop_index(op.f("idx_task_status"), table_name="task")
    op.drop_index(op.f("idx_task_step_id"), table_name="task")
    op.drop_column("task", "archived_status")

    # -------------------------------------------------------------------------
    # task_comment
    # -------------------------------------------------------------------------
    op.execute(
        text(
            """
            UPDATE task_comment
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )
    )

    op.alter_column("task_comment", "comment", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("task_comment", "task_id", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "task_comment",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.alter_column(
        "task_comment", "created_by", existing_type=sa.VARCHAR(), nullable=False
    )

    # old enum is now unused → safe to drop
    sa.Enum(
        "DRAFT",
        "PENDING",
        "IN_PROGRESS",
        "SKIPPED",
        "DONE",
        "ARCHIVED",
        name="taskstatus",
    ).drop(op.get_bind())


def downgrade() -> None:
    # recreate old enum
    sa.Enum(
        "DRAFT",
        "PENDING",
        "IN_PROGRESS",
        "SKIPPED",
        "DONE",
        "ARCHIVED",
        name="taskstatus",
    ).create(op.get_bind())

    op.alter_column("task_comment", "created_by", nullable=True)
    op.alter_column("task_comment", "created_at", nullable=True)
    op.alter_column("task_comment", "task_id", nullable=True)
    op.alter_column("task_comment", "comment", nullable=True)

    op.add_column(
        "task",
        sa.Column(
            "archived_status",
            postgresql.ENUM(
                "DRAFT",
                "PENDING",
                "IN_PROGRESS",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="taskstatus",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.create_index(op.f("idx_task_step_id"), "task", ["step_id"])
    op.create_index(op.f("idx_task_status"), "task", ["status"])
    op.alter_column("task", "updated_at", nullable=True)
    op.alter_column("task", "created_at", nullable=True)

    op.alter_column(
        "task",
        "status",
        type_=postgresql.ENUM(
            "DRAFT",
            "PENDING",
            "IN_PROGRESS",
            "SKIPPED",
            "DONE",
            "ARCHIVED",
            name="taskstatus",
        ),
        postgresql_using="status::taskstatus",
    )

    op.drop_column("task", "previous_status")

    op.alter_column("tag", "value", nullable=True)

    op.add_column(
        "step",
        sa.Column(
            "archived_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.create_index(op.f("idx_step_project_id"), "step", ["project_id"])
    op.alter_column("step", "updated_at", nullable=True)
    op.alter_column("step", "created_at", nullable=True)
    op.drop_column("step", "previous_status")

    op.add_column(
        "project",
        sa.Column(
            "archived_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.alter_column("project", "allow_skip", nullable=True)
    op.alter_column("project", "empty_annotations", nullable=True)
    op.alter_column("project", "is_published", nullable=True)
    op.alter_column("project", "description", nullable=True)
    op.drop_column("project", "previous_status")

    op.add_column(
        "annotation",
        sa.Column(
            "archived_status",
            postgresql.ENUM(
                "DRAFT",
                "IN_PROGRESS",
                "PENDING",
                "SKIPPED",
                "DONE",
                "ARCHIVED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("idx_annotation_user_status"),
        "annotation",
        ["user_email", "annotation_status"],
    )
    op.create_index(op.f("idx_annotation_user_email"), "annotation", ["user_email"])
    op.create_index(op.f("idx_annotation_status"), "annotation", ["annotation_status"])
    op.drop_column("annotation", "previous_status")
