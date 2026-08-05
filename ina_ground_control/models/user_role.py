"""
Define the SQLModel association model between users and roles.

This module includes the definition of the UserRole model, which links a User
to a Role and records assignment metadata (when and by whom the role was
assigned).

Classes:
    UserRole (SQLModel): SQLModel association model between User and Role.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel


class UserRole(SQLModel, table=True):
    """Association table between User and Role."""

    __tablename__ = "user_role"
    __table_args__ = (UniqueConstraint("user_email", "role_id", name="uq_user_role"),)

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True),
    )

    user_email: str = Field(
        sa_column=Column(
            String,
            ForeignKey("user.email"),
            index=True,
            nullable=False,
        )
    )

    role_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("role.id"),
            index=True,
            nullable=False,
        )
    )

    assigned_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )

    assigned_by: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    # Relationships (adjust import paths in your project)
    user: "User" = Relationship(
        sa_relationship=relationship("User", back_populates="user_roles")
    )
    role: "Role" = Relationship(
        sa_relationship=relationship("Role", back_populates="user_roles")
    )
