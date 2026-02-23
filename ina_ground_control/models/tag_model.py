"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the tag model.
The Tag model represents a tag record in the database and includes various attributes
such as value and relationships with other models like Project.

Classes:
    Tag (Base): SqlAlchemy model representing a tag record in the database.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.models import Base


class Tag(Base):
    """
    Represents a tag record in the database.

    Attributes:
        key (Mapped[str]): The unique identifier of the media (Primary Key).
        value (Mapped[str]): The value of the tag.
        project_id (Mapped[int | None]): ForeignKey relationship to the Project model.

    """

    __tablename__ = "tag"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id"))
