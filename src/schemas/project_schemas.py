"""
Defines Data Transfer Object (DTO) classes for project-related data structures.
"""

from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProjectBaseDto(BaseModel):
    """
    Base DTO for project objects.
    """
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    annotation_type: Optional[str]
    is_published: Optional[bool]
    empty_annotations: Optional[bool]
    allow_skip: Optional[bool]
    control_weights: Optional[int]
    pinned_at: Optional[datetime]
    created_by: int

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
    """
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tasks: list[TaskBaseDto] = []
    total_users_with_annotations: int
    total_tasks: int

    class Config:
        from_attributes = True


class ProjectListDto(ProjectWithIdDto):
    """
    DTO for listing projects, including a list of tasks.
    """
    tasks: list[TaskListDto] = []


from .task_schemas import TaskBaseDto, TaskListDto
