"""
Defines Data Transfer Object (DTO) classes for user-related data structures.
"""

from __future__ import annotations

from.user_base_schemas import UserBaseDto
from.project_schemas import ProjectDetailDto
from.task_schemas import TaskListDto


class UserDto(UserBaseDto):
    """
    DTO representing a user object, extending UserBaseDto with associated projects.
    """
    projects: list[ProjectDetailDto] = []

    class Config:
        orm_mode = True


class UserWithTasksDto(UserDto):
    """
    DTO representing a user object with associated tasks.
    """
    tasks: list[TaskListDto] = []
