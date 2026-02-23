"""
This module defines the AnnotationTask model, which describes the relationship
between annotations and tasks in the database, and includes an enumeration for
specifying the direction of the relationship.
"""

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.constants.enums import InOutEnum
from ina_ground_control.models import Base


class AnnotationTask(Base):
    """
    Represents the relationship between an annotation object and a task object.

    Attributes:
    -----------
    annotation_id (Mapped[int]): Identifier of the annotation object.
    task_id (Mapped[int]): Identifier of the task object.
    direction (Mapped[InOutEnum]): Describes the direction of the relationship
                                   (whether the annotation is input or output).
    """

    __tablename__ = "annotation_task"

    annotation_id: Mapped[int] = mapped_column(
        ForeignKey("annotation.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    direction: Mapped[InOutEnum] = mapped_column(Enum(InOutEnum), nullable=False)
