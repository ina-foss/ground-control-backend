"""
This module provides CRUD operations for tasks.

It includes functions to retrieve a task by ID, create a new task, and update an existing task.
"""

from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from ina_ground_control import logger
from ina_ground_control.services.step_service import finish_step
from ina_ground_control.services.annotation_service import get_annotations_by_task_id_crud
from ina_ground_control.schemas.task_schemas import TaskCreateDto
from ina_ground_control.models.annotation_model import AnnotationStatus
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.models.task_model import Task, TaskStatus
from ina_ground_control.exception.exceptions import GroundControlException, ErrorCode


def get_task_by_id(db: Session, task_id: int) -> Task:
    """
    Retrieve a task by its ID.

    Attributes:
        db (Session): The database session used for querying.
        task_id (int): The unique identifier of the task to retrieve.

    Returns:
        Task: The Task object if found, otherwise None.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        logger.error("Failed to retrieve task with id: %d", task_id)
        raise GroundControlException(ErrorCode.RESOURCE_NOT_FOUND, resource="Task", id=task_id)
    return task


def create_task_crud(task: TaskCreateDto, db: Session):
    """
    Create a new task in the database.

    Attributes:
        task (TaskCreateDto): The task data transfer object containing task details.
        db (Session): The database session used for querying.

    Returns:
        Task: The newly created Task object.
    """
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def finish_task(db: Session, task_id: int):
    finished_task = None
    task = get_task_by_id(db,task_id)
    if task.step.allow_empty_annotation :
        print("WIP")
    else :
        finished_annotation_from_task = get_annotations_by_task_id_crud(db,task_id,None,InOutEnum.OUT,AnnotationStatus.DONE)
        if len(finished_annotation_from_task) == task.redundancy :
            finished_task = update_task_status_crud(db ,task.id,TaskStatus.DONE)
            finish_step(db,task.step_id)

    return finished_task


def undone_task(db, task_id: int ):
    updated_task = None
    task = get_task_by_id(db,task_id)
    finished_annotation_from_task = get_annotations_by_task_id_crud(db,task_id,None,InOutEnum.OUT,AnnotationStatus.DONE)
    if len(finished_annotation_from_task) < task.redundancy :
        updated_task = update_task_status_crud(db ,task.id,TaskStatus.PENDING)
    return updated_task

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


def delete_task_crud(db: Session, task: Task):
    """
    Delete a task from the database

    Attributes:
        db (Session): The database session used for querying.
        task_id (int): The unique identifier of the task to update.

    Returns:
        Task: The deleted Task object if the task exists, otherwise None.
    """
    if task is not None:
        db.delete(task)
        db.commit()
    return task


def update_task_status_crud(db: Session, task_id: int, status: TaskStatus ) -> Task:
    task = get_task_by_id(db, task_id)
    task.status = status
    task.updated_at = func.now()
    db.commit()
    db.refresh(task)
    return task
