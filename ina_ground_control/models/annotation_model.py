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

from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.constants.enums import Status
from ina_ground_control.models import Base


class Annotation(Base):
    """
    Represents an annotation record in the database.

    Attributes:
        id (Mapped[int]): The unique identifier of the annotation (Primary Key).
        user_email (Mapped[str]): The email address of the author of the annotation.
        result (Mapped[Optional[dict]]): The result of the annotation.
        annotation_status (Mapped[Status]): The status of the annotation.
        previous_status (Mapped[Optional[Status]]): The archived status of the annotation.
        version (Mapped[int]): The version of the annotation.
        created_at (Mapped[DateTime]): The timestamp when the annotation was created.
        updated_at (Mapped[Optional[DateTime]]): The timestamp when the annotation was last updated.
        validated_at (Mapped[Optional[DateTime]]): The timestamp when the annotation was validated.
    """

    __tablename__ = "annotation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(
        String, ForeignKey("user.email"), nullable=False
    )
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    annotation_status: Mapped[Status] = mapped_column(Enum(Status))
    previous_status: Mapped[Optional[Status]] = mapped_column(
        Enum(Status), nullable=True, default=None
    )
    skipped_by: Mapped[str] = mapped_column(String, nullable=True, default=None)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    validated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
