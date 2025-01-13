"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the taskComment model.
The TaskComment model represents a taskComment record in the database and includes various attributes
such as comment and relationships with other models like Task.

Classes:
    TaskComment (Base): SqlAlchemy model representing a taskComment record in the database.
"""
from ina_ground_control.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql.expression import func

class TaskComment(Base):
    """
    Represents a taskComment record in the database.

    Attributes:
        id (Integer): The unique identifier of the taskComment (Primary Key).
        comment (String): The comment related to the task.
        task_id (Integer): The foreign key linking to the concerned task.

    """
    __tablename__ = "task_comment"

    id = Column(Integer, primary_key=True)
    comment = Column(String)
    task_id = Column(Integer, ForeignKey("task.id"))
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String, ForeignKey("user.email"))

