"""
Defines Data Transfer Object (DTO) classes for step-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ina_ground_control.constants.enums import AnnotationType, Status


class StepCreate(BaseModel):
    """
    DTO to create a step object
    """

    title: str
    description: Optional[str]
    annotation_type: AnnotationType
    pinned_at: Optional[datetime]
    status: Status
    project_id: int
    redundancy: int = Field(default=1, description="Number of annotations per task")
    completeness_rate: float = Field(
        default=100.0, ge=0, le=100, description="Must be between 0 and 100"
    )
    allow_empty_annotation: bool = Field(
        default=False, description="Allow empty annotations"
    )
    max_tasks_per_person: int = Field(default=1, ge=1, description="Must be at least 1")


class StepDto(StepCreate):
    """
    DTO representing a step object, including association with task and project.
    """

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class StepDetailDto(StepDto):
    """
    DTO representing the step object with its related tasks objects.

    Used in `/{project_id}` view
    """

    tasks: Optional[list["TaskWithIdDto"]]
    plugins: Optional[list["PluginWithIdDto"]]


class StepProjectDto(BaseModel):
    annotation_type: AnnotationType
    project: ProjectWithIdDto


class StepPluginDto(BaseModel):
    plugins: PluginWithIdDto


class StepSummaryDto(BaseModel):
    id: int
    annotation_type: str


from ina_ground_control.schemas.plugin_schemas import PluginWithIdDto
from ina_ground_control.schemas.project_schemas import ProjectWithIdDto
from ina_ground_control.schemas.task_schemas import TaskWithIdDto
