"""
This module provides CRUD operations for taskComments.

It includes functions to retrieve a taskComment by ID, create a new taskComment, and update an existing taskComment.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.taskComment_model import TaskComment
from ina_ground_control.schemas.taskComment_schemas import TaskCommentCreate , TaskCommentDto


def get_taskComment_by_id(db: Session, taskComment_id: int):
    """
    Retrieve a taskComment by its ID.

    Attributes:
        db (Session): The database session used for querying.
        id (int): The unique identifier of the taskComment to retrieve.

    Returns:
        TaskComment: The taskComment object if found, otherwise None.
    """
    return db.query(TaskComment).filter(TaskComment.id == taskComment_id).first()

def create_taskComment_crud(taskComment: TaskCommentCreate, db: Session):
    """
    Create a new taskComment in the database.

    Attributes:
        taskComment (TaskCommentCreate): The taskComment data transfer object containing taskComment details.
        db (Session): The database session used for querying.

    Returns:
        TaskComment: The newly created TaskComment object.
    """
    db_taskComment = TaskComment(**taskComment.model_dump())
    db.add(db_taskComment)
    db.commit()
    db.refresh(db_taskComment)
    return db_taskComment

def update_taskComment_crud(taskComment_id:int, taskComment: TaskCommentDto, db: Session):
    """
    Update the data of an existing taskComment in the database.

    Attributes:
        taskComment_id (int): The unique identifier of the taskComment to update.
        taskComment (TagCreate): A new url for the taskComment.
        db (Session): The database session used for querying.

    Returns:
        TaskComment: The updated TaskComment object if the taskComment exists, otherwise None.
    """
    db_taskComment = get_taskComment_by_id(db, taskComment_id)
    if db_taskComment is not None:
        for key, value in taskComment.model_dump().items():
            setattr(db_taskComment, key, value)
        db.commit()
        db.refresh(db_taskComment)
    return db_taskComment

def delete_taskComment_crud(db: Session, taskComment_id:int):
    """
    Delete a taskComment from the database.

    Parameters:
    db (Session): The database session used for querying.
    taskComment_id (int): The unique identifier of the taskComment to delete.

    Returns:
    TaskComment: The deleted TaskComment object if the taskComment exists, otherwise None.
    """
    db_taskComment = db.query(TaskComment).filter(TaskComment.id == taskComment_id).first()
    if db_taskComment is not None:
        db.delete(db_taskComment)
        db.commit()
    return db_taskComment

def get_taskComments(db: Session, skip: int = 0, limit: int = 100):
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