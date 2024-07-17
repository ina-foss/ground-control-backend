"""
Defines Data Transfer Object (DTO) classes for task-related data structures.
"""

from .project_schemas import ProjectBaseDto
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from .annotation_schemas import AnnotationDto
from ina_ground_control.models.task_model import TaskStatus,TaskDataType

class TaskBaseDto(BaseModel):
    """
    Base DTO for task objects.
    """

    name: str
    instruction: Optional[str] = ""
    project_id: int
    data: Optional[str]
    data_type: TaskDataType
    status: TaskStatus
    lead_time: Optional[int]
    step_id: int
    media_id: int

    class Config:
        from_attributes = True


class TaskWithIdDto(TaskBaseDto):
    """
    Extends TaskBaseDto with an additional id field.
    """

    id: int


class TaskCreateDto(TaskBaseDto):
    """
    DTO for creating new task instances.
    Includes all fields from TaskBaseDto plus an optional
     data field for additional task-specific data.
    """

    data: Optional[Dict[str, Any]] = []


class TaskListDto(TaskCreateDto):
    """
    DTO for listing tasks, extending TaskCreateDto with additional
     fields relevant for listing tasks.
    """

    id: int
    project: Optional["ProjectBaseDto"] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    annotations: list[AnnotationDto] = []
    taskComments:list[TaskCreateDto] = []
