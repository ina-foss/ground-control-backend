"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the Task model and related enums.
The Task model represents a task record in the database and includes various attributes
such as name, instruction, data, and relationships with other models like
Annotation and TaskComment. The module also defines the TaskDataType and the TaskStatus enums to represent
the data type and the status of a task.

Classes:
    TaskStatus (PyEnum): Enum representing the different statuses a task can have.
    TaskDataType (PyEnum): Enum representing the different data type a task can have.
    Task (Base): SqlAlchemy model representing a task record in the database.
"""

# pylint: disable=unsubscriptable-object
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    and_,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ina_ground_control.constants.enums import Status, TaskDataType
from ina_ground_control.models import Base
from ina_ground_control.models.annotation_task_association import AnnotationTask
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.task_comment_model import TaskComment


class Task(Base):
    """
    Represents a task record in the database.

    Attributes:
        id (Integer): The unique identifier of the task (Primary Key).
        name (String): The name of the task.
        instruction (String): Instructions for completing the task.
        data_type (TaskDataType): The data type of the task.
        status (Status): The status of the task.
        lead_time (Integer): Lead time of the task.
        created_at (DateTime): The timestamp when the task was created.
        updated_at (DateTime): The timestamp when the task was last updated.
        step_id (Integer): The foreign key linking to the step of the task.
        media_id (Integer): The foreign key linking to the media the task belongs to.
        annotations (relationship): Relationship to the Annotation model representing annotations
            for the task.
        task_comments (relationship): Relationship to the TaskComment model representing task_comments
            for the task.
    """

    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    instruction: Mapped[str | None] = mapped_column(String, default="")
    data_type: Mapped[TaskDataType | None] = mapped_column(Enum(TaskDataType))
    status: Mapped[Status | None] = mapped_column(Enum(Status))
    previous_status: Mapped[Status | None] = mapped_column(Enum(Status), default=None)
    documentation: Mapped[str | None] = mapped_column(String)
    lead_time: Mapped[int | None] = mapped_column(Integer)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    redundancy: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    step_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("step.id"))
    media_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("media.id"))

    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation",
        secondary=AnnotationTask.__table__,
        primaryjoin=and_(
            AnnotationTask.direction == "OUT", AnnotationTask.task_id == id
        ),
        secondaryjoin="Annotation.id == AnnotationTask.annotation_id",
        backref="task",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    task_comments: Mapped[list["TaskComment"]] = relationship(
        "TaskComment", backref="task", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("redundancy >= 1", name="check_redundancy_min"),
        CheckConstraint(
            "priority BETWEEN 0 AND 100", name="check_priority_range"
        ),  # 0 to 100
    )
