from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from .user_base_schemas import UserBaseDto
from .project_schemas import ProjectDetailDto
from .task_schemas import TaskListDto



class UserDto(UserBaseDto):

    projects: list[ProjectDetailDto]= []

    class Config:
        orm_mode: True



class UserWithTasksDto(UserDto):
    tasks: list[TaskListDto] = []

