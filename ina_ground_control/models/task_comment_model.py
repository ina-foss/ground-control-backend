"""
Define the SqlAlchemy models and enums for the project management application.

This module includes the definition of the taskComment model.
The TaskComment model represents a taskComment record in the database and includes various attributes
such as comment and relationships with other models like Task.

Classes:
    TaskComment (Base): SqlAlchemy model representing a taskComment record in the database.
"""

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ina_ground_control.models import Base


class TaskComment(Base):
    """
    Represents a taskComment record in the database.

    Attributes:
        id (Mapped[int]): The unique identifier of the taskComment (Primary Key).
        comment (Mapped[str]): The comment related to the task.
        task_id (Mapped[int]): The foreign key linking to the concerned task.
        created_at (Mapped[DateTime]): The timestamp when the taskComment was created.
        created_by (Mapped[str]): The email of the user who created the comment.
    """

    __tablename__ = "task_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(String)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[str] = mapped_column(String, ForeignKey("user.email"))
