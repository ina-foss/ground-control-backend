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

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from ina_ground_control.database import Base
from enum import Enum as PyEnum


class AnnotationType(PyEnum):
    """
    Enum representing the different types of annotations.

    Attributes:
        SEGMENTATION (str): The annotation type for segmentation tasks.
        TRANSCRIPTION (str): The annotation type for transcription tasks.
    """
    SEGMENTATION = "segmentation"
    TRANSCRIPTION = "transcription"


class Step(Base):
    """
    Represents a step record in the database.

    Attributes:
        id (Integer): The unique identifier of the step (Primary Key).
        title (String): The title of the step.
        description (String): The description of the step.
        status (enumerate): The status of the step.
        annotation_type (enumerate): The annotation type of the step.
        pinned_at (DateTime): The timestamp when the step was pinned.
        created_at (DateTime): The timestamp when the step was created.
        updated_at (DateTime): The timestamp when the step was last updated.
        project_id (Integer): The foreign key linking to the concerned project.
        tasks (relationship): Relationship to the Task model representing tasks within the step.
    """
    __tablename__ = "step"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))
    tasks = relationship("Task", backref="step", cascade="all, delete-orphan")




