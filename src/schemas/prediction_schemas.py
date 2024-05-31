"""
Defines Data Transfer Object (DTO) classes for prediction-related data structures.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class PredictionDto(BaseModel):
    """
    DTO representing a prediction object, including  association with a task and project.
    """
    id: int
    model_name: Optional[str]
    model_version: Optional[str]
    result: Optional[Dict[str, Any]]
    score: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    task_id: int
    project_id: int
