from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from .user_base_schemas import UserBase
from .project_schemas import ProjectDetail
from .task_schemas import TaskList



class User(UserBase):

    projects: list[ProjectDetail]= []

    class Config:
        orm_mode: True



class UserWithTasks(User):
    tasks: list[TaskList] = []

