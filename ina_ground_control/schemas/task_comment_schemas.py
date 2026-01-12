"""
Defines Data Transfer Object (DTO) classes for taskComment-related data structures.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCommentCreate(BaseModel):
    """
    DTO to create a taskComment object
    """

    comment: Optional[str]
    task_id: int
    created_by: str


class TaskCommentDto(TaskCommentCreate):
    """
    DTO representing a taskComment object, including association with task.
    """

    id: int
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
