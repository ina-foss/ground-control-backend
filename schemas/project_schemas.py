from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .task_schemas import TaskBase, TaskList

class ProjectBase(BaseModel):
    title: Optional[str]
    description: Optional[str]
    created_by: int

    class Config:
        orm_mode: True


class ProjectDetail(ProjectBase):
    projectid: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tasks: list[TaskBase] = []  
    total_tasks: int  

    class Config:
        orm_mode: True

class ProjectList(ProjectBase):
    tasks: list[TaskList] = []

    