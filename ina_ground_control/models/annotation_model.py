"""
This module defines the Annotation model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.sql.expression import func
from ina_ground_control.database import Base
from enum import Enum as PyEnum
class AnnotationStatus(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"

class Annotation(Base):
    """
    Represents an annotation record in the database.

    Attributes:
        id (Integer): The unique identifier of the annotation.
        user_email (String): The email address of the author of the annotation.
        result (JSON): The result of the annotation stored as JSON.
        created_at (DateTime): The timestamp when the annotation was created.
        updated_at (DateTime): The timestamp when the annotation was last updated.
        validated_at (DateTime): The timestamp when the annotation was validated.
        task_id (Integer): The foreign key linking to the task associated with the annotation.
        project_id (Integer): The foreign key linking to the project associated with the annotation.
        status (String): The current status of the annotation.
        user (relationship): Relationship to the User model.
    """

    __tablename__ = "annotation"

    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey("user.email"), nullable=False)
    result = Column(String)
    annotation_status = Column(Enum(AnnotationStatus))
    version = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    validated_at = Column(DateTime)
    task_id = Column(Integer, ForeignKey("task.id"))
