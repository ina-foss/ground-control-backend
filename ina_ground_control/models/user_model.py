"""
This module defines the User model for the application.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from ina_ground_control.database import Base


class User(Base):
    """
    Represents a user record in the database.

    Attributes:
        id (Integer): The unique identifier of the user.
        email (String): The email address of the user.
        role (String): The role assigned to the user.
        created_at (DateTime): The timestamp when the user account was created.
        projects (relationship): Relationship to the Project model representing
         projects owned by the user.
    """

    __tablename__ = "user"

    email = Column(String, primary_key=True, unique=True, nullable=False)
    role = Column(String)
    created_at = Column(DateTime)

    projects = relationship("Project", back_populates="owner")
