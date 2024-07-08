"""
Defines Data Transfer Object (DTO) classes for media-related data structures.
"""

from pydantic import BaseModel
from .project_schemas import ProjectBaseDto
from .task_schemas import TaskBaseDto
from typing import Optional


class MediaCreate(BaseModel):
    """
    DTO to create a media object
    """

    url: str
    projects: Optional[list[ProjectBaseDto]]
    tasks: Optional[list[TaskBaseDto]]

class MediaDto(MediaCreate):
    """
    DTO representing a media object, including association with task and project.
    """

    id: int

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
