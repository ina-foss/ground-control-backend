"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the media model.
The Media model represents a media record in the database and includes various attributes
such as url and relationships with other models like Project and Task.

Classes:
    Media (SQLModel): SQLModel model representing a media record in the database.
"""

from typing import Optional

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from ina_ground_control.constants.enums import MediaType
from ina_ground_control.models.task_model import Task


class Media(SQLModel, table=True):
    """
    Represents a media record in the database.

    Attributes:
        id (int): The unique identifier of the media (Primary Key).
        url (str): The URL of the media.
        type (MediaType): The type of the media.
        player_parameters (Optional[dict]): Configuration options for the media player.
        details (Optional[dict]): Additional metadata or details about the media.
        tasks (Relationship): Relationship to the Task model representing tasks within the media.
    """

    __tablename__ = "media"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    url: str = Field(sa_column=Column(String, nullable=False))
    type: MediaType = Field(sa_column=Column(Enum(MediaType), nullable=False))
    player_parameters: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    details: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    tasks: list["Task"] = Relationship(
        sa_relationship=relationship("Task", backref="media", cascade="all")
    )
