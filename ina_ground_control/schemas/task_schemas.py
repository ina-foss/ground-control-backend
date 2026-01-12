"""
Defines Data Transfer Object (DTO) classes for task-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from ina_ground_control.models.task_model import TaskDataType, TaskStatus

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

    model_config = ConfigDict(from_attributes=True)


class TaskWithIdDto(TaskBaseDto):
    """
    Extends TaskBaseDto with an additional id field.
    """

    id: int
    created_at: Optional[datetime]
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
    annotations: list[AnnotationWithIdDto]

    model_config = ConfigDict(from_attributes=True)


from .media_schemas import MediaDto
from .step_schemas import StepProjectDto


class PaginatedTasksDTO(BaseModel):
    """
    DTO for handling paginated task request results.
    Contains a list of task requests and the total number of records available.
    """

    task_requests: List[TaskListDto]
    total_records: int


class ExpirationDateUpdateDto(BaseModel):
    expiration_date: datetime
