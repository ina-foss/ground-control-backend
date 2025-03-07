"""
This module defines Pydantic schemas for creating and handling the
AnnotationTask association between annotations and tasks, including the
direction of the relationship.
"""

from pydantic import BaseModel

from ina_ground_control.models.annotation_task_association import InOutEnum


class AnnotationTaskCreate(BaseModel):
    """
    Schema for creating an AnnotationTask, representing the relationship
    between an annotation and a task.

    Attributes:
    -----------
    annotation_id (int): Identifier of the annotation object.
    task_id (int): Identifier of the task object.
    direction (InOutEnum): Describes whether the annotation is input or output.
    """

    annotation_id: int
    task_id: int
    direction: InOutEnum
