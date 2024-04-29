from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .annotation_schemas import *
from .prediction_schemas import *

class TaskBaseDto(BaseModel):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    project_id: int

    class Config:
        orm_mode = True

class TaskListDto(TaskBaseDto):  
    name: Optional[str]
    instruction: Optional[str]
    annotations: list[AnnotationDto] = []
    predictions: list[PredictionDto] = []

    
class TaskDetailDto(TaskListDto):
    data: Optional[Dict[str, Any]]= []
