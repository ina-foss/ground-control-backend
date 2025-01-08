"""
This module provides CRUD operations for taskComments.

It includes functions to retrieve a taskComment by ID, create a new taskComment, and update an existing taskComment.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.task_comment_model import TaskComment
from ina_ground_control.schemas.task_comment_schemas import TaskCommentCreate, TaskCommentDto


def get_task_comment_by_id(db: Session, task_comment_id: int):
    """
    Retrieve a taskComment by its ID.

    Attributes:
        db (Session): The database session used for querying.
        id (int): The unique identifier of the taskComment to retrieve.

    Returns:
        TaskComment: The taskComment object if found, otherwise None.
    """
    return db.query(TaskComment).filter(TaskComment.id == task_comment_id).first()

def get_task_comment_by_task_id(db: Session, task_comment_task_id: int):
    """
    Retrieve a list of taskComments that match the task_id value.

    Attributes:
        db (Session): The database session used for querying.
        task_comment_task_id (int): The id of the task which all taskComments should reffered to.

    Returns:
        List[TaskComment]: The list of all the TaskComments that match the task_id input.
    """
    return db.query(TaskComment).filter(TaskComment.task_id == task_comment_task_id).all()


def create_task_comment_crud(task_comment: TaskCommentCreate, db: Session):
    """
    Create a new taskComment in the database.

    Attributes:
        task_comment (TaskCommentCreate): The taskComment data transfer object containing taskComment details.
        db (Session): The database session used for querying.

    Returns:
        TaskComment: The newly created TaskComment object.
    """
    db_task_comment = TaskComment(**task_comment.model_dump())
    db.add(db_task_comment)
    db.commit()
    db.refresh(db_task_comment)
    return db_task_comment


def update_task_comment_crud(task_comment_id:int, task_comment: TaskCommentDto, db: Session):
    """
    Update the data of an existing taskComment in the database.

    Attributes:
        task_comment_id (int): The unique identifier of the taskComment to update.
        task_comment (TagCreate): A new url for the taskComment.
        db (Session): The database session used for querying.

    Returns:
        TaskComment: The updated TaskComment object if the taskComment exists, otherwise None.
    """
    db_task_comment = get_task_comment_by_id(db, task_comment_id)
    if db_task_comment is not None:
        for key, value in task_comment.model_dump().items():
            setattr(db_task_comment, key, value)
        db.commit()
        db.refresh(db_task_comment)
    return db_task_comment


def delete_task_comment_crud(db: Session, task_comment_id:int):
    """
    Delete a taskComment from the database.

    Parameters:
    db (Session): The database session used for querying.
    taskComment_id (int): The unique identifier of the taskComment to delete.

    Returns:
    TaskComment: The deleted TaskComment object if the taskComment exists, otherwise None.
    """
    db_task_comment = db.query(TaskComment).filter(TaskComment.id == task_comment_id).first()
    if db_task_comment is not None:
        db.delete(db_task_comment)
        db.commit()
    return db_task_comment


def get_task_comments(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of taskComments from the database with optional pagination.

    Parameters:
    db (Session): The database session used for querying.
    skip (int): The number of records to skip for pagination. Default is 0.
    limit (int): The maximum number of records to return. Default is 100.

    Returns:
    List[TaskComment]: A list of taskComment objects.
    """
    return db.query(TaskComment).offset(skip).limit(limit).all()
