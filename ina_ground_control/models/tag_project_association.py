"""
This module defines the TagProject model, which represents the association
between a tag and a project in the database.
"""

from sqlalchemy import Column, Integer, ForeignKey, String
from ina_ground_control.database import Base

class TagProject(Base):
    """
    TagProject model that defines the relationship between tags and projects.

    Attributes:
    -----------
    tag_key (String): Key of the tag.
    project_id (Integer): Identifier of the project.
    """

    __tablename__ = "tag_project"

    tag_key = Column(String, ForeignKey("tag.key"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
