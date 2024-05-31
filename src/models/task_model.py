"""
This module defines the Task model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Task(Base):
    """
    Represents a task record in the database.

    Attributes:
        id (Integer): The unique identifier of the task.
        name (String): The name of the task.
        instruction (String): Instructions for completing the task.
        created_at (DateTime): The timestamp when the task was created.
        updated_at (DateTime): The timestamp when the task was last updated.
        data (JSON): Additional data associated with the task.
        project_id (Integer): The foreign key linking to the project the task belongs to.
        annotations (relationship): Relationship to the Annotation model representing annotations
         for the task.
    """

    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    instruction = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    data = Column(JSON)
    project_id = Column(Integer, ForeignKey('project.id'))

    annotations = relationship("Annotation", backref="task")
    # predictions = relationship("Prediction", backref="task")
