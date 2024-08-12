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

from ina_ground_control.database import Base
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, and_
from sqlalchemy.orm import backref, relationship, foreign, remote
from sqlalchemy.sql import and_

from ina_ground_control.models.annotation_task_association import Annotation_Task


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
    Enum representing the different statuses a task can have.

    Attributes:
        DRAFT (str): The task is in draft status.
        PENDING (str): The task is pending and awaiting further actions.
        ENDED (str): The task has ended.
    """

    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"


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
    lead_time = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    step_id = Column(Integer, ForeignKey("step.id"))
    media_id = Column(Integer, ForeignKey("media.id"))

    # project = relationship(
    #     "Project", secondary='step', primaryjoin="Task.step_id==Step.id", secondaryjoin="Step.project_id == Project.id", viewonly=True
    # )
    annotations = relationship(
        "Annotation",
        secondary=Annotation_Task.__table__,
        primaryjoin=and_(
            Annotation_Task.direction == 'OUT',
            Annotation_Task.task_id == id
        ),
        secondaryjoin="Annotation.id == Annotation_Task.annotation_id",
        backref="task",
        cascade='all, delete-orphan',
        single_parent= True
    )

    task_comments = relationship(
        "TaskComment", backref="task", cascade="all, delete-orphan"
    )
