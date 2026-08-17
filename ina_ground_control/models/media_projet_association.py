"""
This module defines the MediaProject model, which represents an association
between Media and Project entities in the database.
"""

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, SQLModel


class MediaProject(SQLModel, table=True):
    """
    MediaProject model that defines the relationship between media and projects.

    Attributes:
        media_id (int): Foreign key referencing the Media entity.
        project_id (int): Foreign key referencing the Project entity.
    """

    __tablename__ = "media_project"

    media_id: int = Field(sa_column=Column(ForeignKey("media.id"), primary_key=True))
    project_id: int = Field(
        sa_column=Column(ForeignKey("project.id"), primary_key=True)
    )
