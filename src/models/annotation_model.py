"""
This module defines the Annotation model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from src.database import Base


class Annotation(Base):
    """
    Represents an annotation record in the database.

    Attributes:
        id (Integer): The unique identifier of the annotation.
        user_id (Integer): The foreign key linking to the user who created the annotation.
        result (JSON): The result of the annotation stored as JSON.
        created_at (DateTime): The timestamp when the annotation was created.
        updated_at (DateTime): The timestamp when the annotation was last updated.
        validated_at (DateTime): The timestamp when the annotation was validated.
        task_id (Integer): The foreign key linking to the task associated with the annotation.
        project_id (Integer): The foreign key linking to the project associated with the annotation.
        status (String): The current status of the annotation.
        user (relationship): Relationship to the User model.
    """

    __tablename__ = 'annotation'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    result = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    validated_at = Column(DateTime)
    task_id = Column(Integer, ForeignKey('task.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    status = Column(String)

    user = relationship("User", backref="annotations")
