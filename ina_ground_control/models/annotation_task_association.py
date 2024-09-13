"""
This module defines the AnnotationTask model, which describes the relationship
between annotations and tasks in the database, and includes an enumeration for
specifying the direction of the relationship.
"""

from sqlalchemy import Column, Enum, ForeignKey, Integer
from enum import Enum as PyEnum
from ina_ground_control.database import Base

class InOutEnum(PyEnum):
    """
    Enum representing the two types of relation between Task and Annotation.

    Attributes
    ----------
    IN (str): The annotation is the initial data of the task,
              which can either come from an algorithm or a previous annotation.
    OUT (str): The annotation is the result of the task, containing the user's work.
    """

    IN = "in"
    OUT = "out"

class AnnotationTask(Base):
    """
    Represents the relationship between an annotation object and a task object.

    Attributes:
    -----------
    annotation_id (Integer): Identifier of the annotation object.
    task_id (Integer): Identifier of the task object.
    direction (Enum): Describes the direction of the relationship
                      (whether the annotation is input or output).
    """

    __tablename__ = "annotation_task"

    annotation_id = Column(Integer, ForeignKey("annotation.id",
                                               ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    direction = Column(Enum(InOutEnum), nullable=False)
