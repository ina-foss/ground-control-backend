"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the tag model.
The Tag model represents a tag record in the database and includes various attributes
such as value and relationships with other models like Project.

Classes:
    Tag (Base): SqlAlchemy model representing a tag record in the database.
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from ina_ground_control.models import Base


class Tag(Base):
    """
    Represents a tag record in the database.

    Attributes:
        key (String): The unique identifier of the media (Primary Key).
        value (String): The value of the tag.
        projects (relationship): Relationship to the Project model representing projects within the tag.

    """

    __tablename__ = "tag"

    key = Column(String, primary_key=True)
    value = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))
