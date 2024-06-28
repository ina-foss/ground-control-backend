"""
This module provides CRUD operations for tasks.

It includes functions to retrieve a task by ID, create a new task, and update an existing task.
"""

from typing import Any, Dict

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from ina_ground_control.models.task_model import Task
from ina_ground_control.schemas.task_schemas import TaskCreateDto


def get_task_by_id(db: Session, task_id: int):
    """
    Retrieve a task by its ID.

    Attributes:
        db (Session): The database session used for querying.
        task_id (int): The unique identifier of the task to retrieve.

    Returns:
        Task: The Task object if found, otherwise None.
    """
    return db.query(Task).filter(Task.id == task_id).first()


def create_task_crud(task: TaskCreateDto, db: Session):
    """
    Create a new task in the database.

    Attributes:
        task (TaskCreateDto): The task data transfer object containing task details.
        db (Session): The database session used for querying.

    Returns:
        Task: The newly created Task object.
    """
    db_task = Task(**jsonable_encoder(task))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_data_task_crud(task_id: int, data: Dict[str, Any], db: Session):
    """
    Update the data of an existing task in the database.

    Attributes:
        task_id (int): The unique identifier of the task to update.
        data (Dict[str, Any]): A dictionary containing the new data for the task.
        db (Session): The database session used for querying.

    Returns:
        Task: The updated Task object if the task exists, otherwise None.
    """
    db_task = get_task_by_id(db, task_id=task_id)
    if db_task is not None:
        db_task.data = data
        db.commit()
        db.refresh(db_task)
    return db_task
