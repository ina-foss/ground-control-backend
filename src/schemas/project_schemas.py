from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .task_schemas import TaskBaseDto, TaskListDto

class ProjectBaseDto(BaseModel):
    title: Optional[str]
    description: Optional[str]
    created_by: int

    class Config:
        orm_mode: True


class ProjectDetailDto(ProjectBaseDto):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tasks: list[TaskBaseDto] = []  
    total_tasks: int  

    class Config:
        orm_mode: True

class ProjectListDto(ProjectBaseDto):
    tasks: list[TaskListDto] = []

    