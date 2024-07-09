"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the media model.
The Media model represents a media record in the database and includes various attributes
such as url and relationships with other models like Project and Task.

Classes:
    Media (Base): SqlAlchemy model representing a media record in the database.
"""
from ina_ground_control.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Media(Base):
    """
    Represents a media record in the database.

    Attributes:
        id (Integer): The unique identifier of the media (Primary Key).
        url (String): The url of the media.
        projects (relationship): Relationship to the Project model representing projects within the media.
        tasks (relationship): Relationship to the Task model representing tasks within the media.

    """
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    url = Column(String,nullable=False)
    projects = relationship("Project", backref="media", cascade="all")
    tasks = relationship("Tasks", backref="media", cascade="all")

