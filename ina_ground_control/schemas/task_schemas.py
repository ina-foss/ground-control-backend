"""
Defines Data Transfer Object (DTO) classes for task-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from ina_ground_control.models.task_model import TaskStatus, TaskDataType
from .annotation_schemas import AnnotationWithIdDto
from .task_comment_schemas import TaskCommentDto

class TaskBaseDto(BaseModel):
    """
    Base DTO for task objects.
    """

    name: str
    instruction: Optional[str] = ""
    data_type: TaskDataType
    status: TaskStatus
    lead_time: Optional[int]
    step_id: int
    media_id: int
    documentation: Optional[str] = ""
    expiration_date: Optional[datetime] = None
    redundancy: int = 1
    priority: int = 0

class Config:
    from_attributes = True


class TaskWithIdDto(TaskBaseDto):
    """
    Extends TaskBaseDto with an additional id field.
    """
    id: int
    annotations: list[AnnotationWithIdDto]


class TaskCreateDto(TaskBaseDto):
    """
    DTO for creating new task instances.
    Includes all fields from TaskBaseDto plus an optional
     data field for additional task-specific data.
    """


class TaskListDto(TaskCreateDto):
    """
    DTO for listing tasks, extending TaskCreateDto with additional
     fields relevant for listing tasks.
    """

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    task_comments: list[TaskCommentDto] = []
    step: Optional[StepProjectDto]
    media: Optional[MediaDto]

    class Config:
        orm_mode: True


from .step_schemas import StepProjectDto
from .media_schemas import MediaDto

class PaginatedTasksDTO(BaseModel):
    """
    DTO for handling paginated task request results.
    Contains a list of task requests and the total number of records available.
    """
    task_requests: List[TaskListDto]
    total_records: int
