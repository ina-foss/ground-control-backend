"""
This module defines the Project model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql.expression import func, select, distinct
from src.database import Base
from .task_model import Task
from .annotation_model import Annotation  # Corrected import path
from .user_model import User


class Project(Base):
    """
    Represents a project record in the database.

    Attributes:
        id (Integer): The unique identifier of the project.
        title (String): The title of the project.
        description (String): The description of the project.
        created_at (DateTime): The timestamp when the project was created.
        updated_at (DateTime): The timestamp when the project was last updated.
        created_by (Integer): The foreign key linking to the user who created the project.
        owner (relationship): Relationship to the User model representing the project owner.
        tasks (relationship): Relationship to the Task model representing tasks within the project.
        total_tasks (column_property): A computed property counting the total number of tasks
        in the project.
        total_users_with_annotations (column_property): A computed property counting the total
        number of distinct users
        with annotations in the project.
    """

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey('user.id'))

    owner = relationship("User", back_populates="projects")

    tasks = relationship('Task', backref="project")

    total_tasks = column_property(
        select(func.count()).where(Task.project_id ==
                                   id).correlate_except(Task).scalar_subquery()
    )

    total_users_with_annotations = column_property(
        select(func.count(distinct(User.id)))
        .join(Annotation)
        .join(Task)
        .where(Task.project_id == id)
        .correlate_except(Task)
        .scalar_subquery()
    )
