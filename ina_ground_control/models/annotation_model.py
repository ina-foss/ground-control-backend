"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the Annotation model and related enums.
The Annotation model represents an annotation record in the database and includes various attributes
such as result and relationships with other models like
User and Task. The module also defines the AnnotationStatus enum to represent
the status of an annotation.

Classes:
    Annotation (SQLModel): SQLModel model representing an annotation record in the database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlmodel import Field, SQLModel

from ina_ground_control.constants.enums import Status


class Annotation(SQLModel, table=True):
    """
    Represents an annotation record in the database.

    Attributes:
        id (int): The unique identifier of the annotation (Primary Key).
        user_email (str): The email address of the author of the annotation.
        result (Optional[dict]): The result of the annotation.
        annotation_status (Status): The status of the annotation.
        previous_status (Optional[Status]): The archived status of the annotation.
        version (int): The version of the annotation.
        created_at (datetime): The timestamp when the annotation was created.
        updated_at (Optional[datetime]): The timestamp when the annotation was last updated.
        validated_at (Optional[datetime]): The timestamp when the annotation was validated.
    """

    __tablename__ = "annotation"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    user_email: str = Field(
        sa_column=Column(String, ForeignKey("user.email"), nullable=False)
    )
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    annotation_status: Status = Field(sa_column=Column(Enum(Status), nullable=False))
    previous_status: Optional[Status] = Field(
        default=None, sa_column=Column(Enum(Status), nullable=True)
    )
    skipped_by: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    version: int = Field(sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    validated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
