"""
Defines Data Transfer Object (DTO) classes for user-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .annotation_schemas import AnnotationCreate
from .project_schemas import ProjectDetailDto
from .task_schemas import TaskListDto
from .user_base_schemas import UserBaseDto


class UserDto(UserBaseDto):
    """
    DTO representing a user object, extending UserBaseDto with associated projects.
    """
    projects: list[ProjectDetailDto] = []
    annotations: list[AnnotationCreate] = []
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserWithTasksDto(UserDto):
    """
    DTO representing a user object with associated tasks.
    """
    tasks: list[TaskListDto] = []
