"""
This module provides CRUD operations for tasks.

It includes functions to retrieve a task by ID, create a new task, and update an existing task.
"""

from typing import Any, Dict, List

from sqlalchemy import func, update
from sqlalchemy.orm import Session

from ina_ground_control import logger
from ina_ground_control.constants.enums import InOutEnum, Status
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.task_model import Task
from ina_ground_control.schemas.task_schemas import TaskBaseDto
from ina_ground_control.services.annotation_service import (
    get_annotations_by_task_id_crud,
)
from ina_ground_control.services.project_service import (
    get_project_by_id,
    update_project_status_crud,
)
from ina_ground_control.services.step_service import (
    get_step_by_id,
    update_step_status_crud,
)


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
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Task", id=task_id
        )
    return task


def create_task_crud(task: TaskBaseDto, db: Session):
    """
    Create a new task in the database.

    Attributes:
        task (TaskBaseDto): The task data transfer object containing task details.
        db (Session): The database session used for querying.

    Returns:
        Task: The newly created Task object.
    """
    db_task = Task(**task.model_dump())
    assert db_task.step_id is not None
    step = get_step_by_id(db, db_task.step_id)
    db_task.redundancy = step.redundancy
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    recalculate_step_status(db, db_task.step_id)
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
        for key, value in data.items():
            if hasattr(db_task, key):
                setattr(db_task, key, value)
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
        assert task.step_id is not None
        recalculate_step_status(db, task.step_id)
    return task


def update_task_status_crud(db: Session, task_id: int, status: Status) -> Task:
    """
    Update the status of a task.
    If the new status is SKIPPED, delete all annotations linked to the task (via AnnotationTask).

    Args:
        db (Session): Database session.
        task_id (int): ID of the task to update.
        status (Status): The new status to set.

    Returns:
        Task: The updated Task object.
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND,
            resource="Task",
            id=task_id,
        )

    task.status = status
    task.updated_at = func.now()
    db.commit()
    db.refresh(task)
    assert task.step_id is not None
    recalculate_step_status(db, task.step_id)
    return task


def update_tasks_status_crud(
    db: Session, tasks_id: List[int], status: Status
) -> List[int]:
    """
    Batch update task status.
    Returns list of task IDs that were successfully updated.
    Assumes all tasks belong to the same step.
    """
    if not tasks_id:
        return []

    # Get step_id from any task
    step = db.query(Task.step_id).filter(Task.id.in_(tasks_id)).first()
    if not step:
        return []

    # Update + return updated task IDs
    result = db.execute(
        update(Task)
        .where(Task.id.in_(tasks_id))
        .values(status=status, updated_at=func.now())
        .returning(Task.id)
    )

    updated_task_ids = [row.id for row in result]
    db.commit()

    # Recalculate once (same step)
    assert step.step_id is not None
    recalculate_step_status(db, step.step_id)
    return updated_task_ids


def activate_task_crud(db: Session, task_id: int) -> Task:
    """
    Activate a task.
    - DRAFT      -> PENDING
    - SKIPPED    -> restore to previous_status (fallback to PENDING)
      and restore annotations to their previous status
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND,
            resource="Task",
            id=task_id,
        )

    if task.status == Status.DRAFT:
        task.status = Status.PENDING
        task.updated_at = func.now()

    elif task.status == Status.SKIPPED:
        for annotation in task.annotations or []:
            assert annotation.previous_status is not None
            annotation.annotation_status = annotation.previous_status
            annotation.previous_status = None
            annotation.skipped_by = None  # type: ignore[assignment]
            annotation.updated_at = func.now()  # type: ignore[assignment]

        assert task.previous_status is not None
        task.status = task.previous_status
        task.previous_status = None
        task.updated_at = func.now()

    db.commit()
    db.refresh(task)
    assert task.step_id is not None
    recalculate_step_status(db, task.step_id)
    return task


def recalculate_task_status(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if task.redundancy == 0:
        print(f"⚠️ Task {task_id} has redundancy = 0. Skipping status update.")
        return

    annotations_done = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, Status.DONE
    )
    annotations_in_progress = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, Status.IN_PROGRESS
    )
    annotations_skipped = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, Status.SKIPPED
    )

    done_count = len(annotations_done)
    in_progress_count = len(annotations_in_progress)
    skipped_count = len(annotations_skipped)
    total_annotations = done_count + in_progress_count + skipped_count

    new_status = task.status

    if total_annotations == 0:
        new_status = Status.PENDING
    elif skipped_count == total_annotations:
        # all skipped
        new_status = Status.SKIPPED
    elif done_count >= task.redundancy:
        new_status = Status.DONE
    elif in_progress_count > 0 or done_count > 0:
        new_status = Status.IN_PROGRESS
    else:
        new_status = Status.PENDING

    if task.status != new_status:
        print(f"🔄 Updating Task {task.id} status: {task.status} → {new_status}")
        update_task_status_crud(db, task.id, new_status)
        assert task.step_id is not None
        recalculate_step_status(db, task.step_id)


def recalculate_step_status(db_session, step_id: int):
    step = get_step_by_id(db_session, step_id)
    tasks = step.tasks

    if not tasks:
        new_status = Status.PENDING
    elif all(task.status == Status.DRAFT for task in tasks):
        new_status = Status.DRAFT
    elif all(task.status == Status.SKIPPED for task in tasks):
        new_status = Status.SKIPPED
    else:
        done_tasks = sum(task.status == Status.DONE for task in tasks)
        pending_tasks = sum(task.status == Status.PENDING for task in tasks)
        in_progress_tasks = sum(task.status == Status.IN_PROGRESS for task in tasks)
        total_active_tasks = done_tasks + pending_tasks + in_progress_tasks

        if total_active_tasks == 0:
            new_status = Status.PENDING
        elif done_tasks == total_active_tasks:
            new_status = Status.DONE
        elif pending_tasks == total_active_tasks:
            new_status = Status.PENDING
        else:
            new_status = Status.IN_PROGRESS

    if step.status != new_status:
        update_step_status_crud(db_session, step, new_status)
        recalculate_project_status(db_session, step.project_id)

    db_session.commit()
    return step


def recalculate_project_status(db_session, project_id: int):
    project = get_project_by_id(db_session, project_id)
    steps = project.steps

    if not steps:
        new_status = Status.PENDING
    elif all(step.status == Status.DRAFT for step in steps):
        new_status = Status.DRAFT
    elif all(step.status == Status.SKIPPED for step in steps):
        new_status = Status.PENDING
    elif all(step.status == Status.DONE for step in steps):
        new_status = Status.DONE
    elif all(step.status == Status.PENDING for step in steps):
        new_status = Status.PENDING
    else:
        new_status = Status.IN_PROGRESS

    if project.status != new_status:
        update_project_status_crud(db_session, project.id, new_status)

    db_session.commit()
    return project
