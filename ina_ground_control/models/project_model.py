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
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from ina_ground_control.database import Base
from ina_ground_control.models.media_projet_association import MediaProject
from ina_ground_control.models.tag_project_association import TagProject
from enum import Enum as PyEnum


class DistributionMode(PyEnum):
    """
    Enum describing the different way of distributing task among users

    Attributes
    ----------
        STATIC (str):
        DYNAMIC (str):
    """
    STATIC = "static"
    DYNAMIC = "dynamic"

class ProjectStatus(PyEnum):
    """
    Enum representing the different statuses a project can have.

    Attributes:
        DRAFT (str): The project is in draft status.
        PENDING (str): The project is pending and awaiting further actions.
        ENDED (str): The project has ended.
    """
    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"


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
        medias  (relationship): Relationship to the Media  model representing medias within the project.
        owner (relationship): Relationship to the User model representing the project owner.
        steps (relationship): Relationship to the Step model representing steps within the project.
        total_tasks (column_property): A computed property counting the total number of tasks
        in the project.
        total_users_with_annotations (column_property): A computed property counting the total
        number of distinct users with annotations in the project.
    """

    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(ProjectStatus), nullable=False)
    distribution_mode = Column(Enum(DistributionMode))
    is_published = Column(Boolean)
    empty_annotations = Column(Boolean)
    allow_skip = Column(Boolean)
    control_weights = Column(Integer)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)

    created_by = Column(String, ForeignKey("user.email"))

    medias = relationship("Media", secondary=MediaProject.__table__, backref="projects", cascade="all")
    tags = relationship("Tag", secondary=TagProject.__table__, backref="project", cascade="all")
    owner = relationship("User", back_populates="projects")
    steps = relationship("Step", backref="project", cascade="all, delete-orphan")

    """total_tasks = column_property(
        select(func.count()).where(Task.project_id ==
                                   id).correlate_except(Task).scalar_subquery()
    )

    total_users_with_annotations = column_property(
        select(func.count(User.email.distinct())).join(Annotation).join(Task).where(
            Task.project_id == id).correlate_except(Task).scalar_subquery()
    )"""
