"""
Defines Data Transfer Object (DTO) classes for media-related data structures.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from ina_ground_control.models.media_model import MediaType


class PlayerParameters(BaseModel):
    """
    DTO for the configuration data of a player_parameters.

    """

    thumbnail_base_url: str = ""
    download_base_url: str = ""
    waveform_base_url: str = ""
    tc_offset: int = 0
    headers: dict[str, str] = {}
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, extra="allow"
    )


class MediaCreate(BaseModel):
    """
    DTO to create a media object
    """

    url: str
    type: MediaType
    player_parameters: Optional[dict] | PlayerParameters = None
    details: Optional[dict] = None


class MediaDto(MediaCreate):
    """
    DTO representing a media object, including association with task and project.
    """

    id: int
    tasks: Optional[list["TaskBaseDto"]]

    model_config = ConfigDict(from_attributes=True)


from .task_schemas import TaskBaseDto
