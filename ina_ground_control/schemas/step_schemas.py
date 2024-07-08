"""
Defines Data Transfer Object (DTO) classes for step-related data structures.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from .project_schemas import ProjectBaseDto
from .task_schemas import TaskBaseDto
from ina_ground_control.models.step_model import AnnotationType,ProjectStatus


class StepCreate(BaseModel):
    """
    DTO to create a step object
    """

    title: str
    description: Optional[str]
    stepStatus: ProjectStatus
    annotation: AnnotationType
    projects: Optional[list[ProjectBaseDto]]
    tasks: Optional[list[TaskBaseDto]]
    pinned_at : Optional[datetime]
    project_id =int
    tasks = Optional[list[TaskBaseDto]]

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
