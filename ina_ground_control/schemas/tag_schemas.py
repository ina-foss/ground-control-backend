"""
Defines Data Transfer Object (DTO) classes for tag-related data structures.
"""

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
