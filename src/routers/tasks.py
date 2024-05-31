"""
This module defines the API endpoints related to task management within the application.
It includes routes for retrieving, creating, and updating tasks, leveraging SQLAlchemy
ORM for database interactions.
Tasks are represented through DTOs (Data Transfer Objects) defined in `task_schemas.py`,
 and business logic is implemented in `task_service.py`.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db

from src.schemas.task_schemas import TaskCreateDto, TaskListDto
from src.services.task_service import get_task_by_id, create_task_crud, update_data_task_crud

router = APIRouter(tags=["task"])


@router.get("/task/{task_id}", response_model=TaskListDto)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a task by its unique identifier.

    Args:
        task_id (int): The unique identifier of the task.

    Returns:
        TaskListDto: The requested task's details.
    Raises:
        HTTPException: If the task is not found.
    """
    task = get_task_by_id(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/task/", response_model=TaskCreateDto)
def create_task(task: TaskCreateDto, db: Session = Depends(get_db)):
    """
    Create a new task.

    Args:
        task (TaskCreateDto): The task data to be created.

    Returns:
        TaskCreateDto: The newly created task's details.
    """
    return create_task_crud(task, db)


@router.patch("/task/{task_id}", response_model=TaskListDto)
def update_data_task(task_id: int, data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Update an existing task by its unique identifier.

    Args:
        task_id (int): The unique identifier of the task to update.
        data (Dict[str, Any]): The updated task data.

    Returns:
        TaskListDto: The updated task's details.
    Raises:
        HTTPException: If the task is not found.
    """
    task = update_data_task_crud(task_id, data, db)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
