"""
Defines base Data Transfer Object (DTO) classes for user-related data structures.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserBaseDto(BaseModel):
    """
    Base DTO representing a user object.
    """
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
