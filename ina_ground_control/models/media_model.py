"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the media model.
The Media model represents a media record in the database and includes various attributes
such as url and relationships with other models like Project and Task.

Classes:
    Media (Base): SqlAlchemy model representing a media record in the database.
"""
from ina_ground_control.database import Base
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import JSON

class MediaType(PyEnum):
    """
    Enum representing the different types a media can have.

    Attributes:
        MP4 (str): The media is a mp4 file.
        HLD (str): The project is a hls file.
    """
    MP4 = "mp4"
    HLS = "hls"

class Media(Base):
    """
    Represents a media record in the database.

    Attributes:
        id (Integer): The unique identifier of the media (Primary Key).
        url (String): The url of the media.
        type (enumerate): the type of the media.
        player_parameters (JSON): Configuration options for the media player.
        details (JSON): Additional metadata or details about the media.
        tasks (relationship): Relationship to the Task model representing tasks within the media.

    """
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    url = Column(String,nullable=False)
    type = Column(Enum(MediaType), nullable=False)
    player_parameters = Column(JSON,nullable=True)
    details = Column(JSON,nullable=True)
    tasks = relationship("Task", backref="media", cascade="all")

