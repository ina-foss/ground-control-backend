"""
This module defines the User model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


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

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    role = Column(String)
    created_at = Column(DateTime)

    projects = relationship("Project", back_populates="owner")
