"""
This module provides CRUD operations for tasks.

It includes functions to retrieve a task by ID, create a new task, and update an existing task.
"""

from collections import defaultdict
from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ina_ground_control import logger
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_model import Annotation, AnnotationStatus
from ina_ground_control.models.annotation_task_association import (
    AnnotationTask,
    InOutEnum,
)
from ina_ground_control.models.project_model import ProjectStatus
from ina_ground_control.models.task_model import Task, TaskStatus
from ina_ground_control.schemas.step_schemas import StepStatus
from ina_ground_control.schemas.task_schemas import TaskCreateDto, TaskListDto
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
        recalculate_step_status(db, task.step_id)
    return task


def update_task_status_crud(db: Session, task_id: int, status: TaskStatus) -> Task:
    """
    Update the status of a task.
    If the new status is SKIPPED, delete all annotations linked to the task (via AnnotationTask).

    Args:
        db (Session): Database session.
        task_id (int): ID of the task to update.
        status (TaskStatus): The new status to set.

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

    if task.status == TaskStatus.SKIPPED:
        if task.annotations:
            for annotation in task.annotations:
                db.delete(annotation)
            db.commit()

    task.status = status
    task.updated_at = func.now()
    db.commit()
    db.refresh(task)
    recalculate_step_status(db, task.step_id)
    return task


def get_tasks_by_annotated_by_crud(
    db: Session,
    email: str,
    page: int = 0,
    size: int = 10,
    task_limit_on: bool = False,
):
    """
    Get prioritized and paginated tasks based on:
    1. IN_PROGRESS tasks where user is in annotated_by array.
    2. IN_PROGRESS tasks where redundancy is not met and expiration is near.
    3. PENDING tasks with high priority and expiration is near.
    """
    try:
        offset = page * size
        eager_options = [joinedload(Task.annotations), joinedload(Task.step)]

        # --- Condition 1: IN_PROGRESS tasks annotated by user ---
        tasks_1 = (
            db.query(Task)
            .join(Task.annotations)  # Join to Annotation via relationship
            .filter(
                Task.status == TaskStatus.IN_PROGRESS,
                Annotation.user_email == email,  # Filter based on email
                Annotation.annotation_status == AnnotationStatus.IN_PROGRESS,
            )
            .options(*eager_options)
            .all()
        )
        # --- Condition 2: Get IN_PROGRESS tasks that haven't yet reached the required redundancy ---
        # and where the current user hasn't already annotated them.
        subquery = (
            select(func.count(Annotation.id))
            .select_from(
                AnnotationTask.__table__.join(
                    Annotation, AnnotationTask.annotation_id == Annotation.id
                )
            )
            .where(
                AnnotationTask.task_id == Task.id,
                Annotation.annotation_status == AnnotationStatus.IN_PROGRESS,
                Annotation.user_email != email,
            )
            .correlate(Task)
            .scalar_subquery()
        )

        tasks_2 = (
            db.query(Task)
            .filter(Task.status == TaskStatus.IN_PROGRESS, subquery < Task.redundancy)
            .options(*eager_options)
            .all()
        )

        # --- Condition 3: Get PENDING tasks that are due soon and have high priority ---
        tasks_3 = (
            db.query(Task)
            .filter(
                Task.status == TaskStatus.PENDING,
                # Task.expiration_date <= today
            )
            .order_by(Task.priority.desc())
            .all()
        )

        # Combine in order of priority: tasks_1 → tasks_2 → tasks_3
        combined = tasks_1 + tasks_2 + tasks_3
        # Deduplicate by ID
        seen = set()
        unique_tasks = []
        for task in combined:
            if task.id not in seen:
                unique_tasks.append(task)
                seen.add(task.id)

        # Group and apply max_task_per_person limit
        if task_limit_on:
            grouped = defaultdict(list)
            for task in unique_tasks:
                if task.step:
                    grouped[task.step.id].append(task)

            # Apply max_task_per_person limit from each step
            limited_tasks = []
            for _, tasks in grouped.items():
                step = tasks[0].step  # All tasks share the same step
                limit = step.max_tasks_per_person or len(tasks)
                limited_tasks.extend(tasks[:limit])
        else:
            limited_tasks = unique_tasks

        # Paginate
        paginated = limited_tasks[offset : offset + size]
        tasks = [
            TaskListDto.model_validate(task, from_attributes=True) for task in paginated
        ]
        total_records = len(limited_tasks)
        return tasks, total_records

    except Exception as e:
        logger.error("Failed to retrieve tasks by annotated_by: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details="Unexpected error while getting tasks",
        ) from e


def recalculate_task_status(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)

    if task.redundancy == 0:
        print(f"⚠️ Task {task_id} has redundancy = 0. Skipping status update.")
        return

    annotations_done = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, AnnotationStatus.DONE
    )
    annotations_in_progress = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, AnnotationStatus.IN_PROGRESS
    )
    annotations_skipped = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, AnnotationStatus.SKIPPED
    )

    done_count = len(annotations_done)
    in_progress_count = len(annotations_in_progress)
    skipped_count = len(annotations_skipped)
    total_annotations = done_count + in_progress_count + skipped_count

    new_status = task.status

    if total_annotations == 0:
        new_status = TaskStatus.PENDING
    elif skipped_count == total_annotations:
        # all skipped
        new_status = TaskStatus.SKIPPED
    elif done_count >= task.redundancy:
        new_status = TaskStatus.DONE
    elif in_progress_count > 0 or done_count > 0:
        new_status = TaskStatus.IN_PROGRESS
    else:
        new_status = TaskStatus.PENDING

    if task.status != new_status:
        print(f"🔄 Updating Task {task.id} status: {task.status} → {new_status}")
        update_task_status_crud(db, task.id, new_status)
        recalculate_step_status(db, task.step_id)


def recalculate_step_status(db_session, step_id: int):
    step = get_step_by_id(db_session, step_id)
    tasks = step.tasks

    if not tasks:
        new_status = StepStatus.PENDING
    elif all(task.status == TaskStatus.DRAFT for task in tasks):
        new_status = StepStatus.DRAFT
    elif all(task.status == TaskStatus.SKIPPED for task in tasks):
        new_status = StepStatus.SKIPPED
    else:
        done_tasks = sum(task.status == TaskStatus.DONE for task in tasks)
        pending_tasks = sum(task.status == TaskStatus.PENDING for task in tasks)
        in_progress_tasks = sum(task.status == TaskStatus.IN_PROGRESS for task in tasks)
        total_active_tasks = done_tasks + pending_tasks + in_progress_tasks

        if total_active_tasks == 0:
            new_status = StepStatus.PENDING
        elif done_tasks == total_active_tasks:
            new_status = StepStatus.DONE
        elif pending_tasks == total_active_tasks:
            new_status = StepStatus.PENDING
        else:
            new_status = StepStatus.IN_PROGRESS

    if step.status != new_status:
        update_step_status_crud(db_session, step, new_status)
        recalculate_project_status(db_session, step.project_id)

    db_session.commit()
    return step


def recalculate_project_status(db_session, project_id: int):
    project = get_project_by_id(db_session, project_id)
    steps = project.steps

    if not steps:
        new_status = ProjectStatus.PENDING
    elif all(step.status == StepStatus.DRAFT for step in steps):
        new_status = ProjectStatus.DRAFT
    elif all(step.status == StepStatus.SKIPPED for step in steps):
        new_status = ProjectStatus.PENDING
    elif all(step.status == StepStatus.DONE for step in steps):
        new_status = ProjectStatus.DONE
    elif all(step.status == StepStatus.PENDING for step in steps):
        new_status = ProjectStatus.PENDING
    else:
        new_status = ProjectStatus.IN_PROGRESS

    if project.status != new_status:
        update_project_status_crud(db_session, project.id, new_status)

    db_session.commit()
    return project
