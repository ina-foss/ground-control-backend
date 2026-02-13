# pylint: disable=unsubscriptable-object
"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the Step model and related enums.
The Step model represents a step record in the database and includes various attributes
such as title, description, status, and relationships with other models like
Project and Task. The module also defines the ProjectStatus and AnnotationType enums to represent
the status and the type of a step.

Classes:
    ProjectStatus (PyEnum): Enum representing the different statuses a step of a project can have.
    AnnotationType (PyEnum): Enum representing the different Annotations a step of a project can have.
    Step (Base): SqlAlchemy model representing a step record in the database.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ina_ground_control.constants.enums import AnnotationType, Status
from ina_ground_control.models import Base


class Step(Base):
    """
    Represents a step record in the database.

    Attributes:
        id (Integer): The unique identifier of the step (Primary Key).
        title (String): The title of the step.
        description (String): The description of the step.
        annotation_type (Enum): The annotation type of the step.
        status (Enum): The status of the step.
        order (Integer): Position of the step within the project, used to sort them.
        pinned_at (DateTime): The timestamp when the step was pinned.
        created_at (DateTime): The timestamp when the step was created.
        updated_at (DateTime): The timestamp when the step was last updated.
        project_id (Integer): The foreign key linking to the concerned project.
        tasks (relationship): Relationship to the Task model representing tasks within the step.
        plugins (relationship): Relationship to the Plugin model.
        redundancy (Integer): Redundancy for each tasks of the step, can be modified inside the task (default: 1).
        completeness_rate (Float): Percentage of completeness (0-100).
        allow_empty_annotation (Boolean): Whether empty annotations are allowed (default: False).
        max_tasks_per_person (Integer): Maximum tasks per person (default: 1, must be at least 1).
    """

    __tablename__ = "step"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, default="")
    annotation_type: Mapped[AnnotationType] = mapped_column(
        Enum(AnnotationType), nullable=False
    )
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    previous_status: Mapped[Status | None] = mapped_column(Enum(Status), default=None)
    order: Mapped[int | None] = mapped_column(Integer)
    pinned_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", backref="step", cascade="all, delete-orphan"
    )
    plugins: Mapped[list["Plugin"]] = relationship(
        "Plugin", backref="step", cascade="all, delete-orphan"
    )
    redundancy: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    completeness_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=100.0
    )
    allow_empty_annotation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    max_tasks_per_person: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    __table_args__ = (
        CheckConstraint(
            "completeness_rate BETWEEN 0 AND 100", name="check_completeness_rate_range"
        ),
        CheckConstraint(
            "max_tasks_per_person >= 1", name="check_max_tasks_per_person_minimum"
        ),
    )
