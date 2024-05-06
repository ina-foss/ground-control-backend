from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .annotation_schemas import *
from .prediction_schemas import *
from .project_schemas import *

class TaskBaseDto(BaseModel):
    name: Optional[str] = ''
    instruction: Optional[str] = ''
    project_id: int


    class Config:
        orm_mode = True

class TaskWithIdDto(TaskBaseDto):
    id: int


class TaskCreateDto(TaskBaseDto):
    data: Optional[Dict[str, Any]]= []


class TaskListDto(TaskCreateDto):  
    id: int
    project: Optional[ProjectBaseDto] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    annotations: list[AnnotationDto] = []
    predictions: list[PredictionDto] = []
