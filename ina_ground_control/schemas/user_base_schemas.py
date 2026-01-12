"""
Defines base Data Transfer Object (DTO) classes for user-related data structures.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseDto(BaseModel):
    """
    Base DTO representing a user object.
    """

    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
