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
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from ina_ground_control.models import Base


class User(Base):
    """
    Represents a user record in the database.

    Attributes:
        email (String): The unique identifier of the user (Primary Key).
        role (String): The role assigned to the user.
        created_at (DateTime): The timestamp when the user account was created.
        updated_at (DateTime): The timestamp when the user account was updated.
        projects (relationship): Relationship to the Project model representing
        projects owned by the user.
        annotations (relationship): Relationship to the Annotation model representing
        annotations owned by the user.
    """

    __tablename__ = "user"

    email = Column(String, primary_key=True, unique=True, nullable=False)
    role = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    projects = relationship("Project", back_populates="owner")
    annotations = relationship(
        "Annotation", backref="user", cascade="all, delete-orphan"
    )


class UserInfo(BaseModel):
    email: Optional[str] = None
    roles: List[str] = []
