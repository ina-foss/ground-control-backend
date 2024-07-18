"""
This module defines the API endpoints related to taskComment management within
the application.
Includes routes for creating, retrieving, and updating taskComments.
Utilizes database sessions for CRUD operations and handles exceptions
appropriately.

Endpoints:
    /taskComment/{taskComment_id}: Retrieves a taskComment by its ID.
    /taskComment/: Creates a new taskComment.
    /taskComment/{taskComment_id}: Updates an existing taskComment by its ID.
    /taskComment/{taskComment_id}: Delete taskComment
    /taskComment/: Retrieves all taskComment
Dependencies:
    - External services: None.
    - Internal utilities: Database session, taskComment service for CRUD operations.

Configuration:
    - Database session configuration and taskComment schemas are defined in the
    `src` module.
"""

from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.models.taskComment_model import TaskComment
from ina_ground_control.schemas.taskComment_schemas import TaskCommentCreate , TaskCommentDto
from ina_ground_control.services.taskComment_service import get_taskComment_by_id, create_taskComment_crud, update_taskComment_crud,delete_taskComment_crud,get_taskComments

logger = get_logger()
router = APIRouter(tags=["taskComment"])

#get taskComment by id
@router.get("/taskComment/{taskComment_id}", response_model=TaskCommentDto)
def read_taskComment(taskComment_id : int, db: Session = Depends(get_db)):
    """
    Retrieve a taskComment by its unique identifier key.

    Args:
        taskComment_id (int): The unique identifier of the taskComment.

    Returns:
        TaskCommentDto: The requested taskComment's details.
    Raises:
        HTTPException: If the taskComment is not found.
    """
    taskComment = get_taskComment_by_id(db, taskComment_id=taskComment_id)
    if taskComment is None:
        logger.error("Failed to retrieve taskComment with id: %d", taskComment_id)
        raise HTTPException(status_code=404, detail="TaskComment not found")
    return taskComment

#add new taskComment
@router.post("/taskComment/", response_model=TaskCommentCreate)
def create_taskComment(taskComment: TaskCommentCreate, db: Session = Depends(get_db)):
    """
    Create a new taskComment.

    Args:
        taskComment (TaskCommentCreate): The taskComment data to be created.

    Returns:
        TaskCommentCreate: The newly created taskComment's details.
    """
    try:
        return create_taskComment_crud(taskComment, db)
    except Exception as e:
        logger.error("Failed to create taskComment: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create taskComment") from e


#update taskComment by id
@router.patch("/taskComment/{taskComment_id}", response_model=TaskCommentDto)
def update_taskComment(taskComment_id: int, taskComment: TaskCommentDto, db: Session = Depends(get_db)):
    """
    Update an existing taskComment by its unique identifier.

    Args:
        taskComment_id (int): The unique identifier of the taskComment to update.
        taskComment (TaskCommentDto): The updated taskComment's value.

    Returns:
        TaskCommentDto: The updated taskComment's details.
    Raises:
        HTTPException: If the taskComment is not found.
    """
    updated_taskComment = update_taskComment_crud(taskComment_id, taskComment, db)
    if updated_taskComment is None:
        logger.error("Failed to update taskComment with id: %d", taskComment_id)
        raise HTTPException(status_code=404, detail="taskComment not found")
    return updated_taskComment

#delete taskComment
@router.delete("/taskComment/{taskComment_id}", status_code=status.HTTP_200_OK,response_model=TaskCommentCreate)
def delete_taskComment(taskComment_id: int, db: Session = Depends(get_db)):
    deleted_taskComment = delete_taskComment_crud(db, taskComment_id)
    if deleted_taskComment is None:
        logger.error("Failed to delete taskComment with id: %d", taskComment_id)
        raise HTTPException(status_code=404, detail="taskComment not found")
    return deleted_taskComment

#get list of taskComment
@router.get("/taskComments/", response_model=list[TaskCommentDto])
def read_taskComments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[TaskComment]:
    """Retrieve a list of taskComments with pagination support."""
    taskComments = get_taskComments(db, skip=skip, limit=limit)
    return taskComments
