"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the user model.
The User model represents a user record in the database and includes various attributes
such as email, role and relationships with other models like Project and Annotation.

Classes:
    User (SQLModel): SQLModel model representing a user record in the database.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """
    SQLModel User model.
    """

    __tablename__ = "user"
    # ``email`` is already the primary key, but the database also carries a
    # separate unique constraint/index ``uq_user_email`` that other tables'
    # foreign keys (annotation, project, task_comment, user_role) depend on.
    # Declare it here so Alembic keeps it in sync instead of trying to drop it.
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    email: str = Field(sa_column=Column(String(255), primary_key=True))
    firstname: Optional[str] = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    lastname: Optional[str] = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    is_active: bool = Field(sa_column=Column(Boolean, default=True, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), onupdate=func.now(), nullable=False
        )
    )
    last_login_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    user_roles: List["UserRole"] = Relationship(
        sa_relationship=relationship(
            "UserRole",
            back_populates="user",
        )
    )

    projects: List["Project"] = Relationship(
        sa_relationship=relationship("Project", back_populates="owner")
    )
    annotations: List["Annotation"] = Relationship(
        sa_relationship=relationship(
            "Annotation", backref="user", cascade="all, delete-orphan"
        )
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


from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.project_model import Project
