"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the tag model.
The Tag model represents a tag record in the database and includes various attributes
such as value and relationships with other models like Project.

Classes:
    Tag (SQLModel): SQLModel model representing a tag record in the database.
"""

from typing import Optional

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """
    Represents a tag record in the database.

    Attributes:
        key (str): The unique identifier of the tag (Primary Key).
        value (str): The value of the tag.
        project_id (Optional[int]): ForeignKey relationship to the Project model.

    """

    __tablename__ = "tag"

    key: str = Field(sa_column=Column(String, primary_key=True))
    value: str = Field(sa_column=Column(String, nullable=False))
    project_id: Optional[int] = Field(
        default=None, sa_column=Column(ForeignKey("project.id"))
    )
