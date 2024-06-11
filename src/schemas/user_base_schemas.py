"""
Defines base Data Transfer Object (DTO) classes for user-related data structures.
"""

from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBaseDto(BaseModel):
    """
    Base DTO representing a user object.
    """
    id: int
    email: EmailStr
    role: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
