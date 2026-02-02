"""
This module defines the TagProject model, which represents the association
between a tag and a project in the database.
"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.models import Base


class TagProject(Base):
    """
    TagProject model that defines the relationship between tags and projects.

    Attributes:
    -----------
    tag_key (Mapped[str]): Key of the tag (Primary Key).
    project_id (Mapped[int]): Identifier of the project (Primary Key).
    """

    __tablename__ = "tag_project"

    tag_key: Mapped[str] = mapped_column(
        String, ForeignKey("tag.key"), primary_key=True
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), primary_key=True
    )
