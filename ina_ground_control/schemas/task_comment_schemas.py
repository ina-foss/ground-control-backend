"""
Defines Data Transfer Object (DTO) classes for taskComment-related data structures.
"""

from typing import Optional
from pydantic import BaseModel


class TaskCommentCreate(BaseModel):
    """
    DTO to create a taskComment object
    """
    comment: Optional[str]
    task_id: int

class TaskCommentDto(TaskCommentCreate):
    """
    DTO representing a taskComment object, including association with task.
    """

    id: int
    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
