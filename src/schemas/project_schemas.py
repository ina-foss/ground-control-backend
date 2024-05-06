from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .task_schemas import TaskBaseDto, TaskListDto

class ProjectBaseDto(BaseModel):
    title: Optional[str]
    description: Optional[str]
    created_by: int
    total_users_with_annotations: int

    class Config:
        orm_mode: True

class ProjectWithIdDto(ProjectBaseDto):
    id: int

class ProjectDetailDto(ProjectWithIdDto):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tasks: list[TaskBaseDto] = []  
    total_tasks: int  

    class Config:
        orm_mode: True

class ProjectListDto(ProjectWithIdDto):
    tasks: list[TaskListDto] = []

    