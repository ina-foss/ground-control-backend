"""
Defines Data Transfer Object (DTO) classes for step-related data structures.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


from ina_ground_control.models.step_model import AnnotationType, StepStatus


class StepCreate(BaseModel):
    """
    DTO to create a step object
    """

    title: str
    description: Optional[str]
    annotation_type: AnnotationType
    pinned_at: Optional[datetime]
    status: StepStatus
    project_id : int


class StepDto(StepCreate):
    """
    DTO representing a step object, including association with task and project.
    """

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """

class StepDetailDto(StepDto):
    """
    DTO representing the step object with its related tasks objects.

    Used in `/{project_id}` view
    """
 
    project: ProjectBaseDto
    tasks: Optional[list["TaskWithIdDto"]]



class StepProjectDto(BaseModel):
    annotation_type: AnnotationType
    project: ProjectWithIdDto

from ina_ground_control.schemas.task_schemas import  TaskWithIdDto
from ina_ground_control.schemas.project_schemas import ProjectBaseDto, ProjectWithIdDto
