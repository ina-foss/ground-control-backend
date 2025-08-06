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

from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Float, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func

from ina_ground_control.database import Base


class AnnotationType(PyEnum):
    """
    Enum representing the different types of annotations.

    Attributes:
        SEGMENTATION (str): The annotation type for segmentation tasks.
        TRANSCRIPTION (str): The annotation type for transcription tasks.
    """
    SEGMENTATION = "segmentation"
    TRANSCRIPTION = "transcription"
    SPAN = "span"
    AUTO_SUMMARY = "auto-summary"


class StepStatus(PyEnum):
    """
    Enum representing the different status of a step.

    Attributes:
        DRAFT (str): The step is in draft status.
        PENDING (str): The step is pending and awaiting further actions.
        IN_PROGRESS (str): Currently being worked on.
        SKIPPED (str): This step has been ignored.
        DONE (str): Successfully completed.
    """
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    SKIPPED = "skipped"
    DONE = "done"




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
        redundancy (Integer): Redundancy for each tasks of the step, can be modified inside the task (default: 1)
        completeness_rate (Float): Percentage of completeness (0-100).
        allow_empty_annotation (Boolean): Whether empty annotations are allowed (default: False).
        max_tasks_per_person (Integer): Maximum tasks per person (default: 1, must be at least 1).
    """

    __tablename__ = "step"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    status = Column(Enum(StepStatus), nullable=False)
    order = Column(Integer)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    tasks = relationship("Task", backref="step", cascade="all, delete-orphan")
    plugins = relationship("Plugin", backref="step", cascade="all, delete-orphan")
    redundancy = Column(Integer, nullable=False, default=1)
    completeness_rate = Column(Float, nullable=False, default=100.0)
    allow_empty_annotation = Column(Boolean, nullable=False, default=True)
    max_tasks_per_person = Column(Integer, nullable=False, default=1)
    __table_args__ = (
        CheckConstraint("completeness_rate BETWEEN 0 AND 100", name="check_completeness_rate_range"),
        CheckConstraint("max_tasks_per_person >= 1", name="check_max_tasks_per_person_minimum"),
    )
