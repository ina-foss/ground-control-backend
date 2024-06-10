"""
Defines Data Transfer Object (DTO) classes for annotation-related data structures.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from .user_base_schemas import UserBaseDto


class AnnotationCreate(BaseModel):
    """
       DTO to create an annotation object
    """
    user_id: int
    task_id: int
    project_id: int
    result: Optional[Dict[str, Any]]
    status: str


class AnnotationDto(AnnotationCreate):
    """
    DTO representing an annotation object, including association with task and project.
    """
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    validated_at: Optional[datetime]
    user: UserBaseDto = {}

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
