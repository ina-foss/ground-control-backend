from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from src.database import get_db
from src.schemas.task_schemas import TaskListDto, TaskCreateDto
from src.services.task_service import get_task_by_id, create_task_crud, update_data_task_crud

logger = get_logger()
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
        logger.error(f"Failed to retrieve task with id: {task_id}")
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
    try:
        return create_task_crud(task, db)
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=400, detail="Failed to create task")


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
        logger.error(f"Failed to update task with id: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    return task
