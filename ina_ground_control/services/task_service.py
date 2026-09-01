"""
This module provides CRUD operations for tasks.

It includes functions to retrieve a task by ID, create a new task, and update an existing task.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from ina_ground_control import logger
from ina_ground_control.constants.enums import (
    ExpirationFilter,
    InOutEnum,
    SearchMode,
    Status,
)
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import AnnotationTask
from ina_ground_control.models.task_model import Task
from ina_ground_control.schemas.task_schemas import TaskBaseDto, TaskListPerStep
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
from ina_ground_control.utils.fuzzy_search import FuzzySearchEngine

# Task textual columns that the ``search`` filter can target. The keys are the
# public field names accepted by the API / services; the values are the columns.
_TASK_SEARCH_COLUMNS = {
    "name": Task.name,
    "instruction": Task.instruction,
    "documentation": Task.documentation,
}


def _resolve_search_columns(search_fields: Optional[list[str]]) -> list:
    """Return the columns to search, defaulting to all when ``search_fields`` is None.

    Raises:
        ValueError: If ``search_fields`` contains an unsupported field name.
    """
    if search_fields is None:
        return list(_TASK_SEARCH_COLUMNS.values())
    invalid = [f for f in search_fields if f not in _TASK_SEARCH_COLUMNS]
    if invalid:
        raise ValueError(
            f"Invalid search field(s): {invalid}. "
            f"Allowed fields: {list(_TASK_SEARCH_COLUMNS)}"
        )
    return [_TASK_SEARCH_COLUMNS[f] for f in search_fields]


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


def _build_step_tasks_filters(
    step_id: int,
    tasks_ids: Optional[list[int]] = None,
    status: Optional[Status] = None,
    expiration: Optional[ExpirationFilter] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    search: Optional[str] = None,
    search_mode: SearchMode = SearchMode.EXACT,
    search_fields: Optional[list[str]] = None,
    annotation_user_email: Optional[str] = None,
    annotation_status: Optional[Status] = None,
    annotation_created_from: Optional[datetime] = None,
    annotation_created_to: Optional[datetime] = None,
    annotation_updated_from: Optional[datetime] = None,
    annotation_updated_to: Optional[datetime] = None,
    annotation_direction: InOutEnum = InOutEnum.OUT,
) -> list:
    """
    Build the list of SQLAlchemy filter clauses used to list the tasks of a step.

    The clauses are cumulative and shared between the count and the paginated
    queries so that both stay perfectly consistent. Only SQL-expressible filters
    live here: the ``exact`` text search is turned into an ``ILIKE`` clause across
    ``name``/``instruction``/``documentation``, whereas the ``fuzzy`` text search
    is intentionally NOT added (it is applied in memory by the service layer).

    The ``annotation_*`` filters keep the tasks that have at least one annotation
    (in the ``annotation_direction`` direction, OUT by default) matching every
    provided annotation criterion (a single ``EXISTS`` correlated subquery, so no
    row duplication).

    Attributes:
        step_id (int): The step whose tasks are listed (always applied).
        tasks_ids (Optional[list[int]]): Restrict to this set of task ids.
        status (Optional[Status]): Exact match on the task status.
        expiration (Optional[ExpirationFilter]): Expiration restriction.
        created_from (Optional[datetime]): Inclusive lower bound on the creation date.
        created_to (Optional[datetime]): Inclusive upper bound on the creation date.
        updated_from (Optional[datetime]): Inclusive lower bound on the update date.
        updated_to (Optional[datetime]): Inclusive upper bound on the update date.
        search (Optional[str]): Text searched in name/instruction/documentation.
        search_mode (SearchMode): ``EXACT`` (SQL ILIKE) or ``FUZZY`` (in memory).
        search_fields (Optional[list[str]]): Subset of name/instruction/documentation
            to search. ``None`` searches them all (only used with ``exact`` here;
            the ``fuzzy`` path forwards it to the search engine).
        annotation_user_email (Optional[str]): Exact match on the annotation author.
        annotation_status (Optional[Status]): Exact match on the annotation status.
        annotation_created_from (Optional[datetime]): Inclusive lower bound on the
            annotation creation date.
        annotation_created_to (Optional[datetime]): Inclusive upper bound on the
            annotation creation date.
        annotation_updated_from (Optional[datetime]): Inclusive lower bound on the
            annotation update date.
        annotation_updated_to (Optional[datetime]): Inclusive upper bound on the
            annotation update date.
        annotation_direction (InOutEnum): Direction of the annotations the other
            ``annotation_*`` filters apply to (defaults to OUT).

    Returns:
        list: The list of filter clauses to pass to ``and_``.
    """
    filters = [Task.step_id == step_id]

    if tasks_ids:
        filters.append(Task.id.in_(tasks_ids))
    if status is not None:
        filters.append(Task.status == status)

    if expiration in (ExpirationFilter.EXPIRED, ExpirationFilter.ACTIVE):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if expiration == ExpirationFilter.EXPIRED:
            # Expired: expiration date strictly before now.
            filters.append(Task.expiration_date < now)
        else:
            # Active: expiration date now/in the future, or no expiration set.
            filters.append(
                or_(Task.expiration_date >= now, Task.expiration_date.is_(None))
            )
    # ExpirationFilter.ALL (or None) adds no expiration restriction.

    # Creation date: inclusive range. Each bound is applied independently so a
    # single bound narrows the query on that side only.
    if created_from is not None:
        filters.append(Task.created_at >= created_from)
    if created_to is not None:
        filters.append(Task.created_at <= created_to)

    # Update date: inclusive range, same independent-bound behaviour.
    if updated_from is not None:
        filters.append(Task.updated_at >= updated_from)
    if updated_to is not None:
        filters.append(Task.updated_at <= updated_to)

    # Exact text search is expressible in SQL; the fuzzy variant is applied in
    # memory by the service layer, so it must not add a clause here.
    if search and search_mode == SearchMode.EXACT:
        like = f"%{search}%"
        columns = _resolve_search_columns(search_fields)
        if columns:
            filters.append(or_(*(column.ilike(like) for column in columns)))

    # Annotation filters: keep tasks having at least one OUT annotation matching
    # every provided criterion, via a single correlated EXISTS subquery.
    annotation_conditions = []
    if annotation_user_email:
        annotation_conditions.append(Annotation.user_email == annotation_user_email)
    if annotation_status is not None:
        annotation_conditions.append(Annotation.annotation_status == annotation_status)
    if annotation_created_from is not None:
        annotation_conditions.append(Annotation.created_at >= annotation_created_from)
    if annotation_created_to is not None:
        annotation_conditions.append(Annotation.created_at <= annotation_created_to)
    if annotation_updated_from is not None:
        annotation_conditions.append(Annotation.updated_at >= annotation_updated_from)
    if annotation_updated_to is not None:
        annotation_conditions.append(Annotation.updated_at <= annotation_updated_to)

    if annotation_conditions:
        filters.append(
            select(AnnotationTask.task_id)
            .join(Annotation, Annotation.id == AnnotationTask.annotation_id)
            .where(
                AnnotationTask.task_id == Task.id,
                AnnotationTask.direction == annotation_direction,
                *annotation_conditions,
            )
            .exists()
        )

    return filters


def _fetch_filtered_tasks_query(db: Session, filters: list):
    """Base query for the tasks of a step.

    Only the relationships required by :class:`TaskListPerStep` (``annotations``
    and ``task_comments``) are eager-loaded, to avoid N+1 while not fetching the
    unused ``step``/``project``/``media`` graphs.
    """
    return (
        db.query(Task)
        .filter(and_(*filters))
        .options(
            selectinload(Task.annotations),
            selectinload(Task.task_comments),
        )
    )


def _fuzzy_ranked_tasks(
    db: Session,
    filters: list,
    search: str,
    min_score: float,
    search_fields: Optional[list[str]] = None,
) -> List[Task]:
    """Load the structurally-filtered tasks and rank them by fuzzy score (best first)."""
    tasks = _fetch_filtered_tasks_query(db, filters).all()
    engine = FuzzySearchEngine(min_score=min_score)
    return [
        result.item
        for result in engine.search_tasks(tasks, search, search_fields=search_fields)
    ]


def count_tasks_by_step_crud(
    db: Session,
    step_id: int,
    tasks_ids: Optional[list[int]] = None,
    status: Optional[Status] = None,
    expiration: Optional[ExpirationFilter] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    search: Optional[str] = None,
    search_mode: SearchMode = SearchMode.EXACT,
    search_fields: Optional[list[str]] = None,
    min_score: float = 70.0,
    annotation_user_email: Optional[str] = None,
    annotation_status: Optional[Status] = None,
    annotation_created_from: Optional[datetime] = None,
    annotation_created_to: Optional[datetime] = None,
    annotation_updated_from: Optional[datetime] = None,
    annotation_updated_to: Optional[datetime] = None,
    annotation_direction: InOutEnum = InOutEnum.OUT,
) -> int:
    """
    Count the tasks of a step matching the given filters.

    For the SQL path (no search or ``exact`` search) a single ``COUNT`` query is
    used. For ``fuzzy`` search the structurally-filtered tasks are ranked in
    memory and the number of matches above ``min_score`` is returned.
    """
    filters = _build_step_tasks_filters(
        step_id,
        tasks_ids=tasks_ids,
        status=status,
        expiration=expiration,
        created_from=created_from,
        created_to=created_to,
        updated_from=updated_from,
        updated_to=updated_to,
        search=search,
        search_mode=search_mode,
        search_fields=search_fields,
        annotation_user_email=annotation_user_email,
        annotation_status=annotation_status,
        annotation_created_from=annotation_created_from,
        annotation_created_to=annotation_created_to,
        annotation_updated_from=annotation_updated_from,
        annotation_updated_to=annotation_updated_to,
        annotation_direction=annotation_direction,
    )
    if search and search_mode == SearchMode.FUZZY:
        return len(_fuzzy_ranked_tasks(db, filters, search, min_score, search_fields))
    return db.query(func.count(Task.id)).filter(and_(*filters)).scalar()


def get_tasks_by_step_crud(
    db: Session,
    step_id: int,
    tasks_ids: Optional[list[int]] = None,
    status: Optional[Status] = None,
    expiration: Optional[ExpirationFilter] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    search: Optional[str] = None,
    search_mode: SearchMode = SearchMode.EXACT,
    search_fields: Optional[list[str]] = None,
    min_score: float = 70.0,
    annotation_user_email: Optional[str] = None,
    annotation_status: Optional[Status] = None,
    annotation_created_from: Optional[datetime] = None,
    annotation_created_to: Optional[datetime] = None,
    annotation_updated_from: Optional[datetime] = None,
    annotation_updated_to: Optional[datetime] = None,
    annotation_direction: InOutEnum = InOutEnum.OUT,
    skip: int = 0,
    limit: int = 100,
) -> List[TaskListPerStep]:
    """
    Retrieve the paginated, filtered tasks of a step.

    Structured filters (and the ``exact`` text search) are applied directly in
    SQL with the serialization relationships eager-loaded to avoid N+1. The
    ``fuzzy`` text search loads the structurally-filtered tasks, ranks them in
    memory (best score first) and paginates the ranked list.
    """
    filters = _build_step_tasks_filters(
        step_id,
        tasks_ids=tasks_ids,
        status=status,
        expiration=expiration,
        created_from=created_from,
        created_to=created_to,
        updated_from=updated_from,
        updated_to=updated_to,
        search=search,
        search_mode=search_mode,
        search_fields=search_fields,
        annotation_user_email=annotation_user_email,
        annotation_status=annotation_status,
        annotation_created_from=annotation_created_from,
        annotation_created_to=annotation_created_to,
        annotation_updated_from=annotation_updated_from,
        annotation_updated_to=annotation_updated_to,
        annotation_direction=annotation_direction,
    )
    if search and search_mode == SearchMode.FUZZY:
        ranked = _fuzzy_ranked_tasks(db, filters, search, min_score, search_fields)
        return ranked[skip : skip + limit]
    return (
        _fetch_filtered_tasks_query(db, filters)
        .order_by(Task.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


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
