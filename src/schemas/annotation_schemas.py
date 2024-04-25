from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from .user_base_schemas import UserBase

class Annotation(BaseModel):
    annotationid: int
    userid: int
    result: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    validated_at: Optional[datetime]
    taskid: int
    projectid: int
    status: str
    user: UserBase

    class Config:
        orm_mode: True