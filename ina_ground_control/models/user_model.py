"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the user model.
The User model represents a user record in the database and includes various attributes
such as email, role and relationships with other models like Project and Annotation.

Classes:
    User (Base): SqlAlchemy model representing a user record in the database.
"""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ina_ground_control.models import Base


class User(Base):
    """
    Represents a user record in the database.

    Attributes:
        email (Mapped[str]): The unique identifier of the user (Primary Key).
        role (Mapped[Optional[str]]): The role assigned to the user.
        created_at (Mapped[Optional[DateTime]]): The timestamp when the user account was created.
        updated_at (Mapped[Optional[DateTime]]): The timestamp when the user account was updated.
        projects (Mapped[List["Project"]]): Relationship to the Project model representing
            projects owned by the user.
        annotations (Mapped[List["Annotation"]]): Relationship to the Annotation model representing
            annotations owned by the user.
    """

    __tablename__ = "user"

    email: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, nullable=False
    )
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner")
    annotations: Mapped[List["Annotation"]] = relationship(
        "Annotation", backref="user", cascade="all, delete-orphan"
    )


class UserInfo(BaseModel):
    """
    A Pydantic model that represents user information.

    Attributes:
        email (Optional[str]): The email of the user.
        roles (List[str]): A list of the roles assigned to the user.
    """

    email: Optional[str] = None
    roles: List[str] = []

from ina_ground_control.models.project_model import Project
from ina_ground_control.models.annotation_model import Annotation
