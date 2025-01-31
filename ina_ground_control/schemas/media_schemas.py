"""
Defines Data Transfer Object (DTO) classes for media-related data structures.
"""
from __future__ import annotations
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional
from ina_ground_control.models.media_model import MediaType


class PlayerParameters(BaseModel):
    """
   DTO for the configuration data of a player_parameters.

   """
    thumbnailBaseUrl: str = ""
    waveForm: str = ""
    tcOffset: str = ""
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='allow'
    )


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
    player_parameters: Optional[dict]|PlayerParameters = None
    details: Optional[dict] = None

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """


from .task_schemas import TaskBaseDto
