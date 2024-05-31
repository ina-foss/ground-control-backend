"""
Defines Data Transfer Object (DTO) classes for annotation-related data structures.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from.user_base_schemas import UserBaseDto


class AnnotationDto(BaseModel):
    """
    DTO representing an annotation object, including association with task and project.
    """
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
        orm_mode = True
