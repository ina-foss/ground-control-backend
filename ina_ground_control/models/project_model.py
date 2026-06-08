"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the Project model and related enums.
The Project model represents a project record in the database and includes various attributes
such as title, description, status, and relationships with other models like
User and Task. The module also defines the ProjectStatus enum to represent
the status of a project.

Classes:
    ProjectStatus (PyEnum): Enum representing the different statuses a project can have.
    Project (Base): SqlAlchemy model representing a project record in the database.
"""

# pylint: disable=unsubscriptable-object
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ina_ground_control.constants.enums import DistributionMode, Status
from ina_ground_control.models import Base
from ina_ground_control.models.media_model import Media
from ina_ground_control.models.media_projet_association import MediaProject
from ina_ground_control.models.step_model import Step
from ina_ground_control.models.tag_model import Tag
from ina_ground_control.models.tag_project_association import TagProject
from ina_ground_control.models.user_model import User


class Project(Base):
    """
    Represents a project record in the database.

    Attributes:
        id (Integer): The unique identifier of the project (Primary Key).
        title (String): The title of the project.
        description (String): The description of the project.
        status (enumerate): The status of the project.
        is_published (Boolean): Indicates if the project is published.
        empty_annotations (Boolean): Indicates if the project has empty annotations.
        allow_skip (Boolean): Indicates if skipping is allowed.
        control_weights (Integer): The control weights for the project.
        pinned_at (DateTime): The timestamp when the project was pinned.
        created_at (DateTime): The timestamp when the project was created.
        updated_at (DateTime): The timestamp when the project was last updated.
        created_by (Integer): The foreign key (email) linking to the user who created the project.
        tags (relationship): Relationship to the Tag model representing tags within the project.
        medias  (relationship): Relationship to the Media model representing medias within the project.
        owner (relationship): Relationship to the User model representing the project owner.
        steps (relationship): Relationship to the Step model representing steps within the project.
    """

    __tablename__ = "project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, default="")
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    previous_status: Mapped[Status | None] = mapped_column(
        Enum(Status), nullable=True, default=None
    )
    distribution_mode: Mapped[DistributionMode | None] = mapped_column(
        Enum(DistributionMode)
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    empty_annotations: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_skip: Mapped[bool] = mapped_column(Boolean, default=False)
    control_weights: Mapped[int | None] = mapped_column(Integer, default=0)
    pinned_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    created_by: Mapped[str | None] = mapped_column(String, ForeignKey("user.email"))

    medias: Mapped[list["Media"]] = relationship(
        "Media",
        secondary=MediaProject.__table__,
        backref="projects",
        cascade="all",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=TagProject.__table__,
        backref="project",
        cascade="all",
    )
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    steps: Mapped[list["Step"]] = relationship(
        "Step",
        backref="project",
        cascade="all, delete-orphan",
    )

    # Example for future computed properties (disabled if not actively used):
    # total_tasks: Mapped[int] = column_property(
    #     select(func.count())
    #     .where(Task.project_id == id)
    #     .correlate_except(Task)
    #     .scalar_subquery()
    # )
    #
    # total_users_with_annotations: Mapped[int] = column_property(
    #     select(func.count(User.email.distinct()))
    #     .join(Annotation)
    #     .join(Task)
    #     .where(Task.project_id == id)
    #     .correlate_except(Task)
    #     .scalar_subquery()
    # )
