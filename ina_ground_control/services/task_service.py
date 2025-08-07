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
    task = get_task_by_id(db, task_id)
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

    if task.status == TaskStatus.DRAFT:
        print(f"⏩ Task {task.id} is in DRAFT. Skipping status update.")
        return

    if task.redundancy == 0:
        print(f"⚠️ Task {task_id} has redundancy = 0. Skipping status update.")
        return

    annotations = get_annotations_by_task_id_crud(
        db, task_id, None, InOutEnum.OUT, AnnotationStatus.DONE
    )
    done_count = len(annotations)

    if done_count == 0:
        new_status = TaskStatus.PENDING
    elif done_count < task.redundancy:
        new_status = TaskStatus.IN_PROGRESS
    else:
        new_status = TaskStatus.DONE

    if task.status != new_status:
        print(f"🔄 Updating Task {task.id} status: {task.status} → {new_status}")
        update_task_status_crud(db, task.id, new_status)
        recalculate_step_status(db, task.step_id)


def recalculate_step_status(db: Session, step_id: int):
    step = get_step_by_id(db, step_id)
    total_tasks = len(
        [
            task
            for task in step.tasks
            if task.status != TaskStatus.SKIPPED and task.status != TaskStatus.DRAFT
        ]
    )
    done_tasks = len([task for task in step.tasks if task.status == TaskStatus.DONE])
    pending_tasks = len(
        [task for task in step.tasks if task.status == TaskStatus.PENDING]
    )

    completion_rate = (done_tasks / total_tasks) * 100 if total_tasks else 0
    new_status = step.status
    # Check if all tasks are PENDING, if so set the step to PENDING
    if pending_tasks == total_tasks:
        new_status = StepStatus.PENDING
    # Some tasks are PENDING and others are DONE or IN_PROGRESS
    elif pending_tasks > 0 and pending_tasks < total_tasks:
        new_status = StepStatus.IN_PROGRESS
    # Check if any task is IN_PROGRESS, if so set the step to IN_PROGRESS
    elif any(task.status == TaskStatus.IN_PROGRESS for task in step.tasks):
        new_status = StepStatus.IN_PROGRESS
    # If completion rate is enough, mark step as DONE
    elif completion_rate >= step.completeness_rate:
        new_status = StepStatus.DONE

    if step.status != new_status:
        print(f"🔄 Updating Step {step.id} status: {step.status} → {new_status}")
        update_step_status_crud(db, step, new_status)
        recalculate_project_status(db, step.project_id)


def recalculate_project_status(db: Session, project_id: int):
    project = get_project_by_id(db, project_id)

    active_steps = [
        step
        for step in project.steps
        if step.status not in (StepStatus.DRAFT, StepStatus.SKIPPED)
    ]

    total_steps = len(active_steps)
    done_steps = len([step for step in active_steps if step.status == StepStatus.DONE])
    pending_steps = len(
        [step for step in active_steps if step.status == StepStatus.PENDING]
    )

    completion_rate = (done_steps / total_steps) * 100 if total_steps else 0

    new_status = project.status

    if total_steps == 0:
        # No active steps — default to PENDING or keep current
        new_status = ProjectStatus.PENDING
    elif pending_steps == total_steps:
        new_status = ProjectStatus.PENDING
    elif any(step.status == StepStatus.IN_PROGRESS for step in active_steps):
        new_status = ProjectStatus.IN_PROGRESS
    elif completion_rate >= 100:
        new_status = ProjectStatus.DONE
    else:
        new_status = ProjectStatus.IN_PROGRESS

    if project.status != new_status:
        print(
            f"🔄 Updating Project {project.id} status: {project.status} → {new_status}"
        )
        update_project_status_crud(db, project.id, new_status)
