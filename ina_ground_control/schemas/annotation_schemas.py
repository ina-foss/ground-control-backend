"""
Defines Data Transfer Object (DTO) classes for annotation-related data structures.
"""

from __future__ import annotations
from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel
from ina_ground_control.models.annotation_model import AnnotationStatus


class AnnotationCreate(BaseModel):
    """
    DTO to create an annotation object
    """

    user_email: str
    task_id: int
    result: Optional[Dict[str, Any]]
    annotation_status: AnnotationStatus
    version: int


class AnnotationDto(AnnotationCreate):
    """
    DTO representing an annotation object, including association with task and project.
    """

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    validated_at: Optional[datetime]

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
