"""
Defines Data Transfer Object (DTO) classes for media-related data structures.
"""
from __future__ import annotations
from pydantic import BaseModel
from .task_schemas import TaskBaseDto
from typing import Optional


class MediaCreate(BaseModel):
    """
    DTO to create a media object
    """

    url: str

class MediaDto(MediaCreate):
    """
    DTO representing a media object, including association with task and project.
    """

    id: int
    tasks: Optional[list[TaskBaseDto]]

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """

