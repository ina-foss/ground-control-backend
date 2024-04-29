from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from .user_base_schemas import UserBaseDto

class AnnotationDto(BaseModel):
    id: int
    user_id: int
    result: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    validated_at: Optional[datetime]
    task_id: int
    project_id: int
    status: str
    user: UserBaseDto

    class Config:
        orm_mode: True
