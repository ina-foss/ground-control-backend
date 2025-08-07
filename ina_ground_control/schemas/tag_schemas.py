"""
Defines Data Transfer Object (DTO) classes for tag-related data structures.
"""

from pydantic import BaseModel


class TagCreate(BaseModel):
    """
    DTO to create a tag object
    """

    key: str
    value: str


class TagDto(TagCreate):
    """
    DTO representing a tag object, including association with projectls.
    """

    project_id: int

    class Config:
        from_attributes = True
        """
            Config for reading attributes from other class.
        """
