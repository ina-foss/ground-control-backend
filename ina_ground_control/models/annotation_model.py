"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the Annotation model and related enums.
The Annotation model represents an annotation record in the database and includes various attributes
such as result and relationships with other models like
User and Task. The module also defines the AnnotationStatus enum to represent
the status of an annotation.

Classes:
    AnnotationStatus (PyEnum): Enum representing the different statuses an annotation can have.
    Annotation (Base): SqlAlchemy model representing an annotation record in the database.
"""

from enum import Enum as PyEnum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql.expression import func

from ina_ground_control.models import Base


class AnnotationStatus(PyEnum):
    """
    Enum representing the different statuses an annotation can have.

    Attributes:

        DRAFT (str): The annotation is in draft status.
        IN_PROGRESS (str): The annotation is currently being worked on.
        PENDING (str): The annotation is pending and awaiting further actions.
        SKIPPED (str): The annotation was skipped.
        DONE (str): The annotation has been completed.
    """

    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"
    SKIPPED = "skipped"
    DONE = "done"


class Annotation(Base):
    """
    Represents an annotation record in the database.

    Attributes:
        id (Integer): The unique identifier of the annotation (Primary Key).
        user_email (String): The email address of the author of the annotation.
        result (String): The result of the annotation.
        annotation_status (enumerate): The status of the annotation.
        version (Integer): The version of the annotation.
        created_at (DateTime): The timestamp when the annotation was created.
        updated_at (DateTime): The timestamp when the annotation was last updated.
        validated_at (DateTime): The timestamp when the annotation was validated.
        task_id (Integer): The foreign key linking to the task associated with the annotation.

    """

    __tablename__ = "annotation"

    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey("user.email"), nullable=False)
    result = Column(JSON)
    annotation_status = Column(Enum(AnnotationStatus))
    version = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    validated_at = Column(DateTime)
