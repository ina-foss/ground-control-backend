"""
Defines Data Transfer Object (DTO) classes for tag-related data structures.
"""

from typing import Optional
from pydantic import BaseModel
from .project_schemas import ProjectBaseDto


class TagCreate(BaseModel):
    """
    DTO to create a tag object
    """
    key: str
    value: str
    projects: Optional[list[ProjectBaseDto]]


class TagDto(TagCreate):
    """
    DTO representing a tag object, including association with projectls.
    """

    key: str
    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
