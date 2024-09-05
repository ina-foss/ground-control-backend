"""
Defines Data Transfer Object (DTO) classes for media-related data structures.
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional
from typing import Optional
from ina_ground_control.models.media_model import MediaType

if TYPE_CHECKING:
    from .task_schemas import TaskBaseDto


class MediaCreate(BaseModel):
    """
    DTO to create a media object
    """

    url: str
    type: MediaType


class MediaDto(MediaCreate):
    """
    DTO representing a media object, including association with task and project.
    """

    id: int
    tasks: Optional[list["TaskBaseDto"]]

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """

