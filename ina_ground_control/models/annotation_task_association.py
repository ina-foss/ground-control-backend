"""
This module defines the AnnotationTask model, which describes the relationship
between annotations and tasks in the database, and includes an enumeration for
specifying the direction of the relationship.
"""

from sqlalchemy import Column, Enum, ForeignKey
from sqlmodel import Field, SQLModel

from ina_ground_control.constants.enums import InOutEnum


class AnnotationTask(SQLModel, table=True):
    """
    Represents the relationship between an annotation object and a task object.

    Attributes:
    -----------
    annotation_id (int): Identifier of the annotation object.
    task_id (int): Identifier of the task object.
    direction (InOutEnum): Describes the direction of the relationship
                           (whether the annotation is input or output).
    """

    __tablename__ = "annotation_task"

    annotation_id: int = Field(
        sa_column=Column(
            ForeignKey("annotation.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    task_id: int = Field(
        sa_column=Column(
            ForeignKey("task.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    direction: InOutEnum = Field(sa_column=Column(Enum(InOutEnum), nullable=False))
