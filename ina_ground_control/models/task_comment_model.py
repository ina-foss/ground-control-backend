"""
Define the SQLModel models and enums for the project management application.

This module includes the definition of the taskComment model.
The TaskComment model represents a taskComment record in the database and includes various attributes
such as comment and relationships with other models like Task.

Classes:
    TaskComment (SQLModel): SQLModel model representing a taskComment record in the database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlmodel import Field, SQLModel


class TaskComment(SQLModel, table=True):
    """
    Represents a taskComment record in the database.

    Attributes:
        id (int): The unique identifier of the taskComment (Primary Key).
        comment (str): The comment related to the task.
        task_id (int): The foreign key linking to the concerned task.
        created_at (datetime): The timestamp when the taskComment was created.
        created_by (str): The email of the user who created the comment.
    """

    __tablename__ = "task_comment"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    comment: str = Field(sa_column=Column(String, nullable=False))
    task_id: int = Field(sa_column=Column(ForeignKey("task.id"), nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    created_by: str = Field(
        sa_column=Column(String, ForeignKey("user.email"), nullable=False)
    )
