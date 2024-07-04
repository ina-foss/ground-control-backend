"""
This module defines the Task model for the application.
"""
from ina_ground_control.database import Base
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship


class TaskDataType(PyEnum):
    LDD = "ldd"
    AMALIA = "amalia"

class TaskStatus(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"

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

    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    instruction = Column(String)
    data = Column(String)
    data_type= Column(Enum(TaskDataType))#, nullable=False
    status = Column(Enum(TaskStatus))
    lead_time = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    step_id = Column(Integer, ForeignKey("step.id"))

    media_id = Column(Integer, ForeignKey("media.id"))
    # TODO: update the alembic model to include cascade field in relations
    annotations = relationship("Annotation", backref="task", cascade="all, delete-orphan")
    task_comments = relationship("TaskComment", backref="task", cascade="all, delete-orphan")
