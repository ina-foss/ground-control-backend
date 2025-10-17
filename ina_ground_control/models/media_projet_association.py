"""
This module defines the MediaProject model, which represents an association
between Media and Project entities in the database.
"""

from sqlalchemy import Column, ForeignKey, Integer

from ina_ground_control.models import Base


class MediaProject(Base):
    """
    MediaProject model that defines the relationship between media and projects.
    """

    __tablename__ = "media_project"

    media_id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
