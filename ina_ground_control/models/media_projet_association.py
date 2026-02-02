"""
This module defines the MediaProject model, which represents an association
between Media and Project entities in the database.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.models import Base


class MediaProject(Base):
    """
    MediaProject model that defines the relationship between media and projects.

    Attributes:
        media_id (Mapped[int]): Foreign key referencing the Media entity.
        project_id (Mapped[int]): Foreign key referencing the Project entity.
    """

    __tablename__ = "media_project"

    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), primary_key=True)
