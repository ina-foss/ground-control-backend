"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the Project model.
The Project model represents a project record in the database and includes various attributes
such as title, description, status, and relationships with other models like
User and Task.

Classes:
    Project (SQLModel): SQLModel model representing a project record in the database.
"""

from datetime import datetime

# pylint: disable=unsubscriptable-object
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from ina_ground_control.constants.enums import DistributionMode, Status
from ina_ground_control.models.media_model import Media
from ina_ground_control.models.media_projet_association import MediaProject
from ina_ground_control.models.step_model import Step
from ina_ground_control.models.tag_model import Tag
from ina_ground_control.models.tag_project_association import TagProject
from ina_ground_control.models.user_model import User


class Project(SQLModel, table=True):
    """
    Represents a project record in the database.

    Attributes:
        id (int): The unique identifier of the project (Primary Key).
        title (str): The title of the project.
        description (str): The description of the project.
        status (Status): The status of the project.
        is_published (bool): Indicates if the project is published.
        empty_annotations (bool): Indicates if the project has empty annotations.
        allow_skip (bool): Indicates if skipping is allowed.
        control_weights (int): The control weights for the project.
        pinned_at (datetime): The timestamp when the project was pinned.
        created_at (datetime): The timestamp when the project was created.
        updated_at (datetime): The timestamp when the project was last updated.
        created_by (str): The foreign key (email) linking to the user who created the project.
        tags (relationship): Relationship to the Tag model representing tags within the project.
        medias  (relationship): Relationship to the Media model representing medias within the project.
        owner (relationship): Relationship to the User model representing the project owner.
        steps (relationship): Relationship to the Step model representing steps within the project.
    """

    __tablename__ = "project"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    title: str = Field(sa_column=Column(String, nullable=False))
    description: str = Field(sa_column=Column(String, default="", nullable=False))
    status: Status = Field(sa_column=Column(Enum(Status), nullable=False))
    previous_status: Optional[Status] = Field(
        default=None, sa_column=Column(Enum(Status), nullable=True)
    )
    distribution_mode: Optional[DistributionMode] = Field(
        default=None, sa_column=Column(Enum(DistributionMode))
    )
    is_published: bool = Field(sa_column=Column(Boolean, default=False, nullable=False))
    empty_annotations: bool = Field(
        sa_column=Column(Boolean, default=False, nullable=False)
    )
    allow_skip: bool = Field(sa_column=Column(Boolean, default=False, nullable=False))
    control_weights: Optional[int] = Field(sa_column=Column(Integer, default=0))
    pinned_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    created_by: Optional[str] = Field(
        default=None, sa_column=Column(String, ForeignKey("user.email"))
    )
    updated_by: Optional[str] = Field(default=None, sa_column=Column(String))
    medias: list["Media"] = Relationship(
        sa_relationship=relationship(
            "Media",
            secondary=MediaProject.__table__,
            backref="projects",
            cascade="all",
        )
    )
    tags: list["Tag"] = Relationship(
        sa_relationship=relationship(
            "Tag",
            secondary=TagProject.__table__,
            backref="project",
            cascade="all",
        )
    )
    owner: "User" = Relationship(
        sa_relationship=relationship("User", back_populates="projects")
    )
    steps: list["Step"] = Relationship(
        sa_relationship=relationship(
            "Step",
            backref="project",
            cascade="all, delete-orphan",
        )
    )
