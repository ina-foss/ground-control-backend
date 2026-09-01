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

from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query, Response
from fastapi_keycloak_middleware import AuthorizationResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.enums import (
    ExpirationFilter,
    InOutEnum,
    SearchMode,
    Status,
    TaskSearchField,
)
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.ina_user_admin.middleware import MatchStrategy
from ina_ground_control.ina_user_admin.middleware.auth_dependencies import (
    CheckPermissionsFromDB,
)
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.schemas.media_schemas import MediaCreate
from ina_ground_control.schemas.task_schemas import (
    TaskBaseDto,
    TaskListDto,
    TaskListPerStep,
    TaskWithIdDto,
)
from ina_ground_control.services.annotation_service import create_annotation_crud
from ina_ground_control.services.media_service import create_media_crud
from ina_ground_control.services.task_service import (
    count_tasks_by_step_crud,
    create_task_crud,
    delete_task_crud,
    get_task_by_id,
    get_tasks_by_step_crud,
    update_data_task_crud,
    update_task_status_crud,
    update_tasks_status_crud,
)

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
    return task


@router.get("/step/{step_id}/tasks", response_model=list[TaskListPerStep])
def read_step_tasks(
    step_id: int,
    response: Response,
    search: str = Query(
        None, description="Text searched in name, instruction or documentation"
    ),
    search_mode: SearchMode = Query(
        SearchMode.EXACT,
        description="'exact' (SQL substring) or 'fuzzy' (typo/accent tolerant)",
    ),
    search_fields: list[TaskSearchField] = Query(
        default_factory=lambda: [TaskSearchField.NAME],
        description=(
            "Restrict the text search to these task fields "
            "(name/instruction/documentation). Default value is name."
        ),
    ),
    min_score: float = Query(
        70.0, ge=0, le=100, description="Minimum similarity score for fuzzy search"
    ),
    tasks_ids: list[int] = Query(None, description="Restrict to this set of task ids"),
    status: Status = Query(None, description="Task status"),
    expiration: ExpirationFilter = Query(
        None, description="Expiration filter: expired, active or all"
    ),
    created_from: datetime = Query(
        None,
        description=(
            "Inclusive lower bound on the creation date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T00:00:00"],
    ),
    created_to: datetime = Query(
        None,
        description=(
            "Inclusive upper bound on the creation date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T23:59:59"],
    ),
    updated_from: datetime = Query(
        None,
        description=(
            "Inclusive lower bound on the update date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T00:00:00"],
    ),
    updated_to: datetime = Query(
        None,
        description=(
            "Inclusive upper bound on the update date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T23:59:59"],
    ),
    annotation_user_email: str = Query(
        None, description="Keep tasks having an annotation from this author"
    ),
    annotation_status: Status = Query(
        None, description="Keep tasks having an annotation with this status"
    ),
    annotation_created_from: datetime = Query(
        None,
        description=(
            "Inclusive lower bound on the annotation creation date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T00:00:00"],
    ),
    annotation_created_to: datetime = Query(
        None,
        description=(
            "Inclusive upper bound on the annotation creation date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T23:59:59"],
    ),
    annotation_updated_from: datetime = Query(
        None,
        description=(
            "Inclusive lower bound on the annotation update date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T00:00:00"],
    ),
    annotation_updated_to: datetime = Query(
        None,
        description=(
            "Inclusive upper bound on the annotation update date. "
            "ISO 8601 format, e.g. 2026-06-07 or 2026-06-07T14:30:00"
        ),
        examples=["2026-06-07T23:59:59"],
    ),
    annotation_direction: InOutEnum = Query(
        InOutEnum.OUT,
        description="Direction of the annotations the annotation_* filters target",
    ),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[TaskListPerStep]:
    """
    Retrieve the paginated tasks of a step, with optional cumulative filters.

    Pagination mirrors the projects listing: ``skip``/``limit`` query params and
    the total number of matching tasks exposed through the ``X-Total-Count``
    response header.

    Args:
        step_id (int): The step whose tasks are listed.
        search (str): Optional text searched in name/instruction/documentation.
        search_mode (SearchMode): ``EXACT`` (SQL substring) or ``FUZZY`` (typo tolerant).
        search_fields (list[TaskSearchField]): Task fields the search targets
            (defaults to name/instruction/documentation when omitted).
        min_score (float): Minimum similarity score for fuzzy search.
        tasks_ids (list[int]): Optional restriction to a set of task ids.
        status (Status): Optional exact match on the task status.
        expiration (ExpirationFilter): Optional expiration restriction.
        created_from (datetime): Optional inclusive lower bound on the creation date.
        created_to (datetime): Optional inclusive upper bound on the creation date.
        updated_from (datetime): Optional inclusive lower bound on the update date.
        updated_to (datetime): Optional inclusive upper bound on the update date.
        annotation_user_email (str): Optional author of an OUT annotation of the task.
        annotation_status (Status): Optional status of an OUT annotation of the task.
        annotation_created_from (datetime): Optional lower bound on the annotation creation date.
        annotation_created_to (datetime): Optional upper bound on the annotation creation date.
        annotation_updated_from (datetime): Optional lower bound on the annotation update date.
        annotation_updated_to (datetime): Optional upper bound on the annotation update date.
        annotation_direction (InOutEnum): Direction (in/out, default out) of the annotations
            targeted by the annotation_* filters.

    Returns:
        list[TaskListPerStep]: The matching tasks for the requested page.
    """
    # Empty selection behaves like "all fields".
    fields = [field.value for field in search_fields] if search_fields else None

    total_count = count_tasks_by_step_crud(
        db,
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
        search_fields=fields,
        min_score=min_score,
        annotation_user_email=annotation_user_email,
        annotation_status=annotation_status,
        annotation_created_from=annotation_created_from,
        annotation_created_to=annotation_created_to,
        annotation_updated_from=annotation_updated_from,
        annotation_updated_to=annotation_updated_to,
        annotation_direction=annotation_direction,
    )
    tasks = get_tasks_by_step_crud(
        db,
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
        search_fields=fields,
        min_score=min_score,
        annotation_user_email=annotation_user_email,
        annotation_status=annotation_status,
        annotation_created_from=annotation_created_from,
        annotation_created_to=annotation_created_to,
        annotation_updated_from=annotation_updated_from,
        annotation_updated_to=annotation_updated_to,
        annotation_direction=annotation_direction,
        skip=skip,
        limit=limit,
    )
    response.headers["X-Total-Count"] = str(total_count)
    return tasks


@router.post("/task", response_model=TaskWithIdDto)
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
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Failed to create task"
        ) from e


@router.post("/step/{step_id}", response_model=TaskWithIdDto)
def task_inject(
    annotation: AnnotationFullCreate,
    task: TaskBaseDto,
    media: MediaCreate,
    step_id: int,
    activate: bool = Query(default=False, description="Whether to activate the task"),
    db: Session = Depends(get_db),
):
    """
    Create a media, a task, and an annotation in one atomic transaction.

    Parameters overwritten:
    - `task.media_id`
    - `annotation.association.task_id`
    - `annotation.association.annotation_id`
    - `activate`: optional flag to activate the task (default: False)
    """
    try:
        # Create Media
        created_media = create_media_crud(media, db)

        # Create Task
        task.media_id = created_media.id
        task.step_id = step_id
        created_task = create_task_crud(task, db)

        # Optionally activate task
        if activate:
            update_task_status_crud(db, created_task.id, Status.PENDING)

        # Create Annotation
        annotation.association.task_id = created_task.id
        create_annotation_crud(db, annotation)

        # Commit all changes only if everything succeeded
        db.commit()
        db.refresh(created_task)

        return created_task

    except IntegrityError as e:
        db.rollback()
        logger.error("Database integrity error: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Database integrity error"
        ) from e

    except Exception as e:
        db.rollback()
        logger.error("An unexpected error occurred: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="An unexpected error occurred"
        ) from e


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
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Task", id=task_id
        )
    return task


@router.delete("/task/{task_id}", response_model=TaskWithIdDto)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissionsFromDB([Permission.DELETE_TASK.value], MatchStrategy.AND)
    ),
    # pylint: disable=invalid-name
) -> TaskWithIdDto:
    """
    Delete a task by ID.

    Args:
        task_id (int): The unique identifier of the task to delete

    Returns:
        TaskWithIdDto: The deleted task
    """
    retrieved_task = get_task_by_id(db, task_id)
    if retrieved_task is None:
        logger.error("Task with id %d not found", task_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Task", id=task_id
        )

    deleted_task = delete_task_crud(db, retrieved_task)
    if deleted_task is None:
        logger.error("Failed to delete task with id: %d", task_id)
        raise GroundControlException(
            ErrorCode.GENERIC_OPERATION_FAILED,
            action="delete",
            resource="task",
            id=task_id,
        )
    return deleted_task


@router.post("/task/{task_id}/status", response_model=TaskListDto)
def update_task_status(task_id: int, status: Status, db: Session = Depends(get_db)):
    task = update_task_status_crud(db, task_id, status)
    return task


@router.post("/tasks/status", response_model=List[int])
def update_tasks_status(
    tasks_id: List[int],
    status: Status,
    db: Session = Depends(get_db),
):
    """
    update tasks status list of tasks.
    """
    return update_tasks_status_crud(db, tasks_id, status)
