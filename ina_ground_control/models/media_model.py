"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the media model.
The Media model represents a media record in the database and includes various attributes
such as url and relationships with other models like Project and Task.

Classes:
    Media (Base): SqlAlchemy model representing a media record in the database.
"""

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ina_ground_control.constants.enums import MediaType
from ina_ground_control.models import Base
from ina_ground_control.models.task_model import Task


class Media(Base):
    """
    Represents a media record in the database.

    Attributes:
        id (Mapped[int]): The unique identifier of the media (Primary Key).
        url (Mapped[str]): The URL of the media.
        type (Mapped[MediaType]): The type of the media.
        player_parameters (Mapped[JSON]): Configuration options for the media player.
        details (Mapped[JSON]): Additional metadata or details about the media.
        tasks (Mapped[Relationship]): Relationship to the Task model representing tasks within the media.
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    player_parameters: Mapped[JSON | None] = mapped_column(JSON, nullable=True)
    details: Mapped[JSON | None] = mapped_column(JSON, nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", backref="media", cascade="all")
