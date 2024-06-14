# Corrected import path
from .task_model import Task
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from .user_model import User
from .annotation_model import Annotation
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql.expression import func, select
from src.database import Base


class ProjectStatus(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"


class AnnotationType(PyEnum):
    SEGMENTATION = "segmentation"
    TRANSCRIPTION = "transcription"


class Project(Base):
    """
    Represents a project record in the database.

    Attributes:
        id (Integer): The unique identifier of the project.
        title (String): The title of the project.
        description (String): The description of the project.
        status (enumerate): The status of the project.
        annotation_type (enumerate): The type of annotation.
        is_published (Boolean): Indicates if the project is published.
        empty_annotations (Boolean): Indicates if the project has empty annotations.
        allow_skip (Boolean): Indicates if skipping is allowed.
        control_weights (Integer): The control weights for the project.
        pinned_at (DateTime): The timestamp when the project was pinned.
        created_at (DateTime): The timestamp when the project was created.
        updated_at (DateTime): The timestamp when the project was last updated.
        created_by (Integer): The foreign key linking to the user who created the project.
        owner (relationship): Relationship to the User model representing the project owner.
        tasks (relationship): Relationship to the Task model representing tasks within the project.
        total_tasks (column_property): A computed property counting the total number of tasks
        in the project.
        total_users_with_annotations (column_property): A computed property counting the total
        number of distinct users with annotations in the project.
    """

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(ProjectStatus), nullable=False)
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    is_published = Column(Boolean)
    empty_annotations = Column(Boolean)
    allow_skip = Column(Boolean)
    control_weights = Column(Integer)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    created_by = Column(String, ForeignKey('user.email'))

    owner = relationship("User", back_populates="projects")
    tasks = relationship('Task', backref="project")

    total_tasks = column_property(
        select(func.count()).where(Task.project_id ==
                                   id).correlate_except(Task).scalar_subquery()
    )

    total_users_with_annotations = column_property(
        select(func.count(User.email.distinct())).join(Annotation).join(Task).where(
            Task.project_id == id).correlate_except(Task).scalar_subquery()
    )
