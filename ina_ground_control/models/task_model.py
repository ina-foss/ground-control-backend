"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the Task model and related enums.
The Task model represents a task record in the database and includes various attributes
such as name, instruction, data, and relationships with other models like
Annotation and TaskComment. The module also defines the TaskDataType and the TaskStatus enums to represent
the data type and the status of a task.

Classes:
    TaskStatus (PyEnum): Enum representing the different statuses a task can have.
    TaskDataType (PyEnum): Enum representing the different data type a task can have.
    Task (Base): SqlAlchemy model representing a task record in the database.
"""

from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_

from ina_ground_control.database import Base
from ina_ground_control.models.annotation_task_association import AnnotationTask


class TaskDataType(PyEnum):
    """
    Enum representing the different datatypes of tasks.

    Attributes:
        LDD (str): The annotation type for ldd tasks.
        AMALIA (str): The annotation type for amalia tasks.
    """

    LDD = "ldd"
    AMALIA = "amalia"


class TaskStatus(PyEnum):
    """
    Enum representing the different status of a task.

    Attributes:
        DRAFT (str): The task is in draft status.
        PENDING (str): The task is pending and awaiting further actions.
        IN_PROGRESS (str): Currently being worked on.
        SKIPPED (str): This task has been ignored.
        DONE (str): Successfully completed.
    """
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    SKIPPED = "skipped"
    DONE = "done"

class Task(Base):
    """
    Represents a task record in the database.

    Attributes:
        id (Integer): The unique identifier of the task (Primary Key).
        name (String): The name of the task.
        instruction (String): Instructions for completing the task.
        data_type (enumerate): The data type of the task.
        status (enumerate): The status of the task.
        lead_time (Integer) : lead time of the task.
        created_at (DateTime): The timestamp when the task was created.
        updated_at (DateTime): The timestamp when the task was last updated.

        step_id (Integer): The foreign key linking to the step of the task.
        media_id (Integer): The foreign key linking to the media the task belongs to.
        annotations (relationship): Relationship to the Annotation model representing annotations
         for the task.
        task_comments (relationship): Relationship to the TaskComment model representing task_comments
         for the task.
    """

    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    instruction = Column(String)
    data_type = Column(Enum(TaskDataType))  # , nullable=False
    status = Column(Enum(TaskStatus))
    documentation = Column(String)
    lead_time = Column(Integer)
    expiration_date = Column(DateTime)
    redundancy = Column(Integer, nullable=False, default=1)
    priority = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    step_id = Column(Integer, ForeignKey("step.id"))
    media_id = Column(Integer, ForeignKey("media.id"))

    annotations = relationship(
        "Annotation",
        secondary=AnnotationTask.__table__,
        primaryjoin=and_(
            AnnotationTask.direction == "OUT",
            AnnotationTask.task_id == id
        ),
        secondaryjoin="Annotation.id == AnnotationTask.annotation_id",
        backref="task",
        cascade="all, delete-orphan",
        single_parent=True
    )

    task_comments = relationship(
        "TaskComment", backref="task", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("redundancy >= 1", name="check_redundancy_min"),  # Min 1 person
        CheckConstraint("priority BETWEEN 0 AND 100", name="check_priority_range"),  # 0 to 100
    )
