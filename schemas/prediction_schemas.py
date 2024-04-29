from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PredictionDto(BaseModel):
    id: int
    model_name: Optional[str]
    model_version: Optional[str]
    result: Optional[Dict[str, Any]]
    score: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    taskid: int
    projectid: int