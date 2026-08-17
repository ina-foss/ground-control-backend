# pylint: disable=unsubscriptable-object
"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the Step model.
The Step model represents a step record in the database and includes various attributes
such as title, description, status, and relationships with other models like
Project and Task.

Classes:
    Step (SQLModel): SQLModel model representing a step record in the database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from ina_ground_control.constants.enums import AnnotationType, Status
from ina_ground_control.models.plugin_model import Plugin
from ina_ground_control.models.task_model import Task


class Step(SQLModel, table=True):
    """
    Represents a step record in the database.

    Attributes:
        id (int): The unique identifier of the step (Primary Key).
        title (str): The title of the step.
        description (str): The description of the step.
        annotation_type (AnnotationType): The annotation type of the step.
        status (Status): The status of the step.
        order (int): Position of the step within the project, used to sort them.
        pinned_at (datetime): The timestamp when the step was pinned.
        created_at (datetime): The timestamp when the step was created.
        updated_at (datetime): The timestamp when the step was last updated.
        project_id (int): The foreign key linking to the concerned project.
        tasks (relationship): Relationship to the Task model representing tasks within the step.
        plugins (relationship): Relationship to the Plugin model.
        redundancy (int): Redundancy for each tasks of the step, can be modified inside the task (default: 1).
        completeness_rate (float): Percentage of completeness (0-100).
        allow_empty_annotation (bool): Whether empty annotations are allowed (default: False).
        max_tasks_per_person (int): Maximum tasks per person (default: 1, must be at least 1).
    """

    __tablename__ = "step"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(sa_column=Column(String, default=""))
    annotation_type: AnnotationType = Field(
        sa_column=Column(Enum(AnnotationType), nullable=False)
    )
    status: Status = Field(sa_column=Column(Enum(Status), nullable=False))
    previous_status: Optional[Status] = Field(
        default=None, sa_column=Column(Enum(Status))
    )
    order: Optional[int] = Field(default=None, sa_column=Column(Integer))
    pinned_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), onupdate=func.now(), nullable=False
        )
    )
    project_id: int = Field(
        sa_column=Column(Integer, ForeignKey("project.id"), nullable=False)
    )
    tasks: list["Task"] = Relationship(
        sa_relationship=relationship(
            "Task", backref="step", cascade="all, delete-orphan"
        )
    )
    plugins: list["Plugin"] = Relationship(
        sa_relationship=relationship(
            "Plugin", backref="step", cascade="all, delete-orphan"
        )
    )
    redundancy: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    completeness_rate: float = Field(
        sa_column=Column(Float, nullable=False, default=100.0)
    )
    allow_empty_annotation: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=True)
    )
    max_tasks_per_person: int = Field(
        sa_column=Column(Integer, nullable=False, default=1)
    )
    settings: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    __table_args__ = (
        CheckConstraint(
            "completeness_rate BETWEEN 0 AND 100", name="check_completeness_rate_range"
        ),
        CheckConstraint(
            "max_tasks_per_person >= 1", name="check_max_tasks_per_person_minimum"
        ),
    )
