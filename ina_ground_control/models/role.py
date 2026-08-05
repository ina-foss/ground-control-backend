"""
Define the SQLModel model for application roles.

This module includes the definition of the Role model, which represents a role
record in the database and its relationship with users through the UserRole
association model.

Classes:
    Role (SQLModel): SQLModel model representing a role record in the database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel


class Role(SQLModel, table=True):
    """
    Represents a role record in the database.

    Attributes:
        id (int): The unique identifier of the role (Primary Key).
        name (str): The unique name of the role.
        description (Optional[str]): An optional description of the role.
        created_at (datetime): The timestamp when the role was created.
        updated_at (datetime): The timestamp when the role was last updated.
        user_roles (Relationship): Relationship to the UserRole association model.
    """

    __tablename__ = "role"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))

    name: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )

    description: Optional[str] = Field(
        default=None, sa_column=Column(String(500), nullable=True)
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), onupdate=func.now(), nullable=False
        )
    )

    user_roles: list["UserRole"] = Relationship(
        sa_relationship=relationship(
            "UserRole",
            back_populates="role",
            cascade="all, delete-orphan",
        )
    )
