"""
This module defines the TagProject model, which represents the association
between a tag and a project in the database.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlmodel import Field, SQLModel


class TagProject(SQLModel, table=True):
    """
    TagProject model that defines the relationship between tags and projects.

    Attributes:
    -----------
    tag_key (str): Key of the tag (Primary Key).
    project_id (int): Identifier of the project (Primary Key).
    """

    __tablename__ = "tag_project"

    tag_key: str = Field(
        sa_column=Column(String, ForeignKey("tag.key"), primary_key=True)
    )
    project_id: int = Field(
        sa_column=Column(Integer, ForeignKey("project.id"), primary_key=True)
    )
