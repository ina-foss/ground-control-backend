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
from ina_ground_control.models.task_comment_model import TaskComment
from ina_ground_control.schemas.task_comment_schemas import TaskCommentCreate , TaskCommentDto
from ina_ground_control.services.task_comment_service import (get_task_comment_by_id, create_task_comment_crud, get_task_comment_by_task_id,
                                                              update_task_comment_crud,
                                                              delete_task_comment_crud,get_task_comments)

logger = get_logger()
router = APIRouter(tags=["taskComment"])

#get taskComment by id
@router.get("/task_comment/{task_comment_id}", response_model=TaskCommentDto)
def read_task_comment(task_comment_id : int, db: Session = Depends(get_db)):
    """
    Retrieve a taskComment by its unique identifier key.

    Args:
        task_comment_id (int): The unique identifier of the taskComment.

    Returns:
        TaskCommentDto: The requested taskComment's details.
    Raises:
        HTTPException: If the taskComment is not found.
    """
    task_comment = get_task_comment_by_id(db, task_comment_id=task_comment_id)
    if task_comment is None:
        logger.error("Failed to retrieve taskComment with id: %d", task_comment_id)
        raise HTTPException(status_code=404, detail="TaskComment not found")
    return task_comment

@router.get("/taskComments/{task_comment_task_id}", response_model=list[TaskCommentDto])
def read_task_comments_by_task_id(task_comment_task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a list of taskComments filtered on their `task_id` value.
    """
    task_comments = get_task_comment_by_task_id(db, task_comment_task_id=task_comment_task_id)
    return task_comments

#add new taskComment
@router.post("/taskComment", response_model=TaskCommentCreate)
def create_task_comment(task_comment: TaskCommentCreate, db: Session = Depends(get_db)):
    """
    Create a new taskComment.

    Args:
        task_comment (TaskCommentCreate): The taskComment data to be created.

    Returns:
        TaskCommentCreate: The newly created taskComment's details.
    """
    try:
        return create_task_comment_crud(task_comment, db)
    except Exception as e:
        logger.error("Failed to create taskComment: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create taskComment") from e


#update taskComment by id
@router.patch("/taskComment/{taskComment_id}", response_model=TaskCommentDto)
def update_task_comment(task_comment_id: int, task_comment: TaskCommentDto, db: Session = Depends(get_db)):
    """
    Update an existing taskComment by its unique identifier.

    Args:
        task_comment_id (int): The unique identifier of the taskComment to update.
        task_comment (TaskCommentDto): The updated taskComment's value.

    Returns:
        TaskCommentDto: The updated taskComment's details.
    Raises:
        HTTPException: If the taskComment is not found.
    """
    updated_task_comment = update_task_comment_crud(task_comment_id, task_comment, db)
    if updated_task_comment is None:
        logger.error("Failed to update taskComment with id: %d", task_comment_id)
        raise HTTPException(status_code=404, detail="taskComment not found")
    return updated_task_comment

#delete taskComment
@router.delete("/taskComment/{taskComment_id}", status_code=status.HTTP_200_OK,response_model=TaskCommentCreate)
def delete_task_comment(task_comment_id: int, db: Session = Depends(get_db)):
    deleted_task_comment = delete_task_comment_crud(db, task_comment_id)
    if deleted_task_comment is None:
        logger.error("Failed to delete taskComment with id: %d", task_comment_id)
        raise HTTPException(status_code=404, detail="taskComment not found")
    return deleted_task_comment

#get list of taskComment
@router.get("/taskComments", response_model=list[TaskCommentDto])
def read_task_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[TaskComment]:
    """Retrieve a list of taskComments with pagination support."""
    task_comments = get_task_comments(db, skip=skip, limit=limit)
    return task_comments
