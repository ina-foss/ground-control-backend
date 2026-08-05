"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the Task model and related enums.
The Task model represents a task record in the database and includes various attributes
such as name, instruction, data, and relationships with other models like
Annotation and TaskComment.

Classes:
    Task (SQLModel): SQLModel model representing a task record in the database.
"""

from datetime import datetime

# pylint: disable=unsubscriptable-object
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    and_,
    func,
)
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from ina_ground_control.constants.enums import Status, TaskDataType
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import AnnotationTask
from ina_ground_control.models.task_comment_model import TaskComment


class Task(SQLModel, table=True):
    """
    Represents a task record in the database.

    Attributes:
        id (int): The unique identifier of the task (Primary Key).
        name (str): The name of the task.
        instruction (str): Instructions for completing the task.
        data_type (TaskDataType): The data type of the task.
        status (Status): The status of the task.
        lead_time (int): Lead time of the task.
        created_at (datetime): The timestamp when the task was created.
        updated_at (datetime): The timestamp when the task was last updated.
        step_id (int): The foreign key linking to the step of the task.
        media_id (int): The foreign key linking to the media the task belongs to.
        annotations (relationship): Relationship to the Annotation model representing annotations
            for the task.
        task_comments (relationship): Relationship to the TaskComment model representing task_comments
            for the task.
    """

    __tablename__ = "task"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    name: str = Field(sa_column=Column(String, nullable=False))
    instruction: Optional[str] = Field(sa_column=Column(String, default=""))
    data_type: Optional[TaskDataType] = Field(
        default=None, sa_column=Column(Enum(TaskDataType))
    )
    status: Optional[Status] = Field(default=None, sa_column=Column(Enum(Status)))
    previous_status: Optional[Status] = Field(
        default=None, sa_column=Column(Enum(Status))
    )
    documentation: Optional[str] = Field(default=None, sa_column=Column(String))
    lead_time: Optional[int] = Field(default=None, sa_column=Column(Integer))
    expiration_date: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime)
    )
    redundancy: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    priority: int = Field(sa_column=Column(Integer, nullable=False, default=0))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), onupdate=func.now(), nullable=False
        )
    )
    step_id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, ForeignKey("step.id"))
    )
    media_id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, ForeignKey("media.id"))
    )

    annotations: list["Annotation"] = Relationship(
        sa_relationship=relationship(
            "Annotation",
            secondary=AnnotationTask.__table__,
            primaryjoin=lambda: and_(
                AnnotationTask.direction == "OUT",
                AnnotationTask.task_id == Task.id,
            ),
            secondaryjoin="Annotation.id == AnnotationTask.annotation_id",
            backref="task",
            cascade="all, delete-orphan",
            single_parent=True,
        )
    )

    task_comments: list["TaskComment"] = Relationship(
        sa_relationship=relationship(
            "TaskComment", backref="task", cascade="all, delete-orphan"
        )
    )

    __table_args__ = (
        CheckConstraint("redundancy >= 1", name="check_redundancy_min"),
        CheckConstraint(
            "priority BETWEEN 0 AND 100", name="check_priority_range"
        ),  # 0 to 100
    )
