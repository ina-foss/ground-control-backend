"""
This module defines the API endpoints related to task management within
the application.
Includes routes for creating, retrieving, and updating tasks.
Utilizes database sessions for CRUD operations and handles exceptions
appropriately.

Endpoints:
    /task/{task_id}: Retrieves a task by its ID.
    /task/: Creates a new task.
    /task/{task_id}: Updates an existing task by its ID.

Dependencies:
    - External services: None.
    - Internal utilities: Database session, task service for CRUD operations.

Configuration:
    - Database session configuration and task schemas are defined in the
    `src` module.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.schemas.media_schemas import MediaCreate
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.schemas.task_schemas import TaskListDto, TaskBaseDto, TaskWithIdDto
from ina_ground_control.services.task_service import get_task_by_id, create_task_crud, update_data_task_crud
from ina_ground_control.services.media_service import create_media_crud
from ina_ground_control.services.annotation_service import create_annotation_crud

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
        logger.error("Failed to retrieve task with id: %d", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/task/", response_model=TaskWithIdDto)
def create_task(task: TaskBaseDto, db: Session = Depends(get_db)):
    """
    Create a new task.

    Args:
        task (TaskBaseDto): The task data to be created.

    Returns:
        TaskBaseDto: The newly created task's details.
    """
    try:
        return create_task_crud(task, db)
    except Exception as e:
        logger.error("Failed to create task: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create task") from e

@router.post("/step/{step_id}", response_model=TaskWithIdDto)
def task_inject(
    annotation: AnnotationFullCreate, 
    task: TaskBaseDto,  
    media: MediaCreate,
    step_id: int,
    db: Session = Depends(get_db)
):
    """
    Use to create a media, a task and an annotation in one request

    List of parameters overwritten by the request
    which can be equal to 0:
    - `task.media_id`
    - `annotation.association.task_id`
    - `annotation.association.annotation_id`

    """
    try:
        # Create Media
        created_media = create_media_crud(media, db)

        # Use the media id for the Task
        task.media_id = created_media.id
        task.step_id = step_id
        created_task = create_task_crud(task, db)

        # Use the task id for the Annotation
        annotation.association.task_id = created_task.id
        created_annotation = create_annotation_crud(db, annotation)

        return created_task

    except IntegrityError as e:
        logger.error("Database integrity error: %s", e)
        raise HTTPException(status_code=400, detail="Database integrity error")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(status_code=400, detail="An unexpected error occurred")


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
        logger.error("Failed to update task with id: %d", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return task
