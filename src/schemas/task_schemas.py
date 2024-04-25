from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .annotation_schemas import *
from .prediction_schemas import *

class TaskBase(BaseModel):
    taskid: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    projectid: int

    class Config:
        orm_mode = True

class TaskList(TaskBase):  
    name: Optional[str]
    instruction: Optional[str]
    annotations: list[Annotation] = []
    predictions: list[Prediction] = []

    
class TaskDetail(TaskList):
    data: Optional[Dict[str, Any]]= []
    