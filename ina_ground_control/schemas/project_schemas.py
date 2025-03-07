"""
Defines Data Transfer Object (DTO) classes for project-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ina_ground_control.models.project_model import ProjectStatus


class ProjectBaseDto(BaseModel):
    """
    Base DTO for project objects.
    """

    title: Optional[str]
    description: Optional[str]
    status: Optional[ProjectStatus]
    is_published: Optional[bool]
    empty_annotations: Optional[bool]
    allow_skip: Optional[bool]
    control_weights: Optional[int]
    pinned_at: Optional[datetime]
    created_by: str

    class Config:
        from_attributes = True


class ProjectWithIdDto(ProjectBaseDto):
    """
    Extends ProjectBaseDto with an additional id field.
    """

    id: int


class ProjectDetailDto(ProjectWithIdDto):
    """
    Detailed DTO for project objects, including creation and update timestamps,
    a list of tasks, and counts of users with annotations and total tasks.

    Used in `/dashboard` view
    """

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    steps: list[StepDto]
    medias: list[MediaCreate]


class ProjectListDto(ProjectWithIdDto):
    """
    DTO for listing projects, including a list of tasks.

    Used in `/{project_id}` view
    """

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    steps: list["StepDetailDto"]
    medias: list[MediaCreate]


from ina_ground_control.schemas.step_schemas import StepDetailDto, StepDto
from ina_ground_control.schemas.media_schemas import MediaCreate
