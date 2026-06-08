"""
Service related to project objects.

Functions:
- get_projects
- get_project_by_id
- create_project_crud
- update_project_crud
- delete_project_crud
"""

import time
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import asc, case, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ina_ground_control import logger
from ina_ground_control.constants.enums import Status
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import AnnotationTask
from ina_ground_control.models.project_model import Project
from ina_ground_control.models.step_model import Step
from ina_ground_control.models.task_model import Task
from ina_ground_control.schemas.project_schemas import ProjectBaseDto


def get_relevant_task_for_user(project, user_email: str):
    """
    Given a project and a user, return the first relevant task to annotate
    according to user role and annotation logic.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    high_priority_tasks = []  # user in-progress
    medium_priority_tasks = []  # available in-progress
    pending_tasks = []  # pending tasks

    for step in project.steps:
        for task in step.tasks:

            # Condition 1: tasks in progress by this user (HIGHEST priority)
            if any(
                ann.user_email == user_email
                and ann.annotation_status == Status.IN_PROGRESS
                for ann in task.annotations
            ):
                high_priority_tasks.append(task)
                # TODO: => continue
                break

            # Condition 2: insufficient redundancy (MEDIUM priority)
            other_anns_in_progress = [
                ann
                for ann in task.annotations
                if ann.annotation_status == Status.IN_PROGRESS
                and ann.user_email != user_email
            ]

            if (
                task.status == Status.IN_PROGRESS
                and len(other_anns_in_progress) < task.redundancy
            ):
                medium_priority_tasks.append(task)
                # TODO: => continue
                break

            # Condition 3: pending tasks
            if task.status == Status.PENDING:
                pending_tasks.append(task)

    # ✅ Sort pending tasks:
    # Order:
    # 1. Expired first
    # 2. Then closest expiration date
    # 3. Then no expiration last

    pending_tasks.sort(
        key=lambda t: (
            t.expiration_date is None,
            t.expiration_date > now if t.expiration_date else True,
            t.expiration_date or datetime.max.replace(tzinfo=timezone.utc),
        )
    )

    all_filtered_tasks = high_priority_tasks + medium_priority_tasks + pending_tasks
    project.tasks_to_annotate = [all_filtered_tasks[0]] if all_filtered_tasks else None
    return project


def get_projects_count(db: Session) -> int:
    """
    Get the total count of projects in the database.

    Parameters:
    db (Session): The database session used for querying.

    Returns:
    int: The total number of projects.
    """
    return db.query(func.count(Project.id)).scalar()


def get_projects_summary(
    db: Session, request: Request, skip: int = 0, limit: int = 100
):
    """
    Optimized query for project summary - only fetches required fields.
    Uses a subquery for steps_count instead of loading all steps.
    """
    start = time.perf_counter()

    # Subquery for steps count
    steps_count_subquery = (
        select(func.count(Step.id))
        .where(Step.project_id == Project.id)
        .correlate(Project)
        .scalar_subquery()
    )

    # Fetch only the columns we need plus the steps count
    results = (
        db.query(
            Project.id,
            Project.created_at,
            Project.created_by,
            Project.title,
            Project.description,
            Project.status,
            steps_count_subquery.label("steps_count"),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info("DB query (summary) took %.3fs", time.perf_counter() - start)

    current_user = request.scope.get("user", {})
    roles = current_user.roles
    user_email = current_user.email
    is_admin = Permission.ADMIN_PROJECT.value in roles

    # For non-admin users, fetch relevant tasks separately
    project_ids = [r.id for r in results]
    tasks_by_project = {}

    if not is_admin and project_ids:
        start = time.perf_counter()
        tasks_by_project = _get_relevant_tasks_for_projects(db, project_ids, user_email)
        logger.info(
            "get_relevant_tasks_for_projects took %.3fs", time.perf_counter() - start
        )

    # Build summary objects
    summaries = []
    for row in results:
        task_ids = tasks_by_project.get(row.id) if not is_admin else None
        summaries.append(
            {
                "id": row.id,
                "created_at": row.created_at,
                "created_by": row.created_by,
                "title": row.title,
                "description": row.description,
                "status": row.status,
                "steps_count": row.steps_count or 0,
                "tasks_id_to_annotate": task_ids,
            }
        )

    return summaries


def _get_relevant_tasks_for_projects(
    db: Session, project_ids: list[int], user_email: str
) -> dict[int, list[int]]:
    """
    Efficiently fetch one relevant task per project for a user.
    Returns a dict mapping project_id -> [task_id] or empty list.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = {}

    # Query 1: Tasks in progress by this user (highest priority)
    in_progress_by_user = (
        db.query(Task.id, Step.project_id)
        .join(Step, Task.step_id == Step.id)
        .join(AnnotationTask, Task.id == AnnotationTask.task_id)
        .join(Annotation, AnnotationTask.annotation_id == Annotation.id)
        .filter(
            Step.project_id.in_(project_ids),
            Annotation.user_email == user_email,
            Annotation.annotation_status == Status.IN_PROGRESS,
        )
        .all()
    )

    for task_id, project_id in in_progress_by_user:
        if project_id not in result:
            result[project_id] = [task_id]

    # Projects that still need a task
    remaining_projects = [pid for pid in project_ids if pid not in result]

    if remaining_projects:
        # Query 2: Tasks with insufficient redundancy
        # Subquery: count of in-progress annotations by other users
        other_ann_count = (
            select(func.count(Annotation.id))
            .select_from(AnnotationTask)
            .join(Annotation, AnnotationTask.annotation_id == Annotation.id)
            .where(
                AnnotationTask.task_id == Task.id,
                Annotation.annotation_status == Status.IN_PROGRESS,
                Annotation.user_email != user_email,
            )
            .correlate(Task)
            .scalar_subquery()
        )

        in_progress_tasks = (
            db.query(Task.id, Step.project_id)
            .join(Step, Task.step_id == Step.id)
            .filter(
                Step.project_id.in_(remaining_projects),
                Task.status == Status.IN_PROGRESS,
                other_ann_count < Task.redundancy,
            )
            .all()
        )

        for task_id, project_id in in_progress_tasks:
            if project_id not in result:
                result[project_id] = [task_id]

    # Update remaining projects list
    remaining_projects = [pid for pid in project_ids if pid not in result]

    if remaining_projects:
        # Query 3: Pending tasks (prioritize expired ones)
        pending_tasks = (
            db.query(Task.id, Step.project_id, Task.expiration_date)
            .join(Step, Task.step_id == Step.id)
            .filter(
                Step.project_id.in_(remaining_projects),
                Task.status == Status.PENDING,
            )
            .order_by(
                Step.project_id,  # group by project
                case(
                    (Task.expiration_date.is_(None), 1),  # NULLs last
                    else_=0,
                ),
                case(
                    (Task.expiration_date <= now, 0),  # expired first
                    else_=1,
                ),
                asc(Task.expiration_date),
            )
            .all()
        )
        for task_id, project_id, expiration_date in pending_tasks:
            if project_id not in result:
                result[project_id] = [task_id]
            elif expiration_date and expiration_date <= now:
                # Expired task takes priority
                result[project_id] = [task_id]

    return result


def get_projects(db: Session, request: Request, skip: int = 0, limit: int = 100):
    start = time.perf_counter()
    projects = (
        db.query(Project)
        .options(
            selectinload(Project.steps)
            .selectinload(Step.tasks)
            .selectinload(Task.annotations),
            selectinload(Project.medias),
            selectinload(Project.tags),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info("DB query took %.3fs", time.perf_counter() - start)

    current_user = request.scope.get("user", {})
    roles = current_user.roles
    user_email = current_user.email

    if Permission.ADMIN_PROJECT.value not in roles:
        start = time.perf_counter()
        for project in projects:
            get_relevant_task_for_user(project, user_email)
        logger.info(
            "get_relevant_task_for_user loop took %.3fs", time.perf_counter() - start
        )

    return projects


def get_project_by_id_based_on_user_role(
    db: Session, request: Request, project_id: int
):
    project = (
        db.query(Project)
        .options(joinedload(Project.steps).joinedload(Step.tasks))
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        logger.error("Failed to retrieve project with id: %d", project_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
        )

    current_user = request.scope.get("user", {})
    user_email = current_user.email

    project = get_relevant_task_for_user(project, user_email)
    return project


def get_project_by_id(db: Session, project_id: int):
    """
    Retrieve a project by its ID, including its tasks.

    Parameters:
    db (Session): The database session used for querying.
    project_id (int): The unique identifier of the project to retrieve.

    Returns:
    Project: The Project object if found, otherwise None.
    """
    return (
        db.query(Project)
        .options(joinedload(Project.steps).joinedload(Step.tasks))
        .filter(Project.id == project_id)
        .first()
    )


def create_project_crud(db: Session, project: ProjectBaseDto):
    """
    Create a new project in the database.

    Parameters:
    db (Session): The database session used for querying.
    project (ProjectBaseDto): The project data transfer object containing project details.

    Returns:
    Project: The newly created Project object.
    """
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project_crud(db: Session, project: ProjectBaseDto, project_id: int):
    """
    Update an existing project in the database.

    Parameters:
    db (Session): The database session used for querying.
    project (ProjectBaseDto): The project data transfer object containing updated project details.
    project_id (int): The unique identifier of the project to update.

    Returns:
    Project: The updated Project object if the project exists, otherwise None.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is not None:
        for key, value in project.model_dump().items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_project_crud(db: Session, project_id: int):
    """
    Delete a project from the database.

    Parameters:
    db (Session): The database session used for querying.
    project_id (int): The unique identifier of the project to delete.

    Returns:
    Project: The deleted Project object if the project exists, otherwise None.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is not None:
        db.delete(db_project)
        db.commit()
    return db_project


def update_project_status_crud(db: Session, project_id: int, status: Status):
    project = get_project_by_id(db, project_id)
    project.status = status
    project.updated_at = func.now()
    db.commit()
    db.refresh(project)
    return project


def get_project_parameters(db: Session, project_id: int):
    step = db.query(Step).filter(Step.project_id == project_id).first()
    project = get_project_by_id(db, project_id)
    if not step or not project:
        return None

    parameters = {
        "redundancy": step.redundancy,
        "completeness_rate": step.completeness_rate,
        "allow_empty_annotation": step.allow_empty_annotation,
        "max_tasks_per_person": step.max_tasks_per_person,
        "allow_skip": project.allow_skip,
    }
    return parameters


def finish_project_service(db: Session, project_id: int):
    """Mark the project and all related steps and tasks as DONE."""
    project = get_project_by_id(db, project_id)
    if not project:
        logger.error("Failed to retrieve project with id: %d", project_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
        )
    if project.status == Status.DONE:
        logger.warning("Project %d is already DONE", project_id)
        raise GroundControlException(
            ErrorCode.BAD_REQUEST,
            action="finish",
            resource="project",
            id_part=f" with id {project_id} (already marked as DONE)",
        )
    project.status = Status.DONE
    project.updated_at = func.now()
    for step in project.steps:
        step.status = Status.DONE
        step.updated_at = func.now()
        for task in step.tasks:
            task.status = Status.DONE
            task.updated_at = func.now()
            for annotation in getattr(task, "annotations", []):
                annotation.annotation_status = Status.DONE
                annotation.updated_at = func.now()
    db.commit()
    db.refresh(project)
    return project


def get_progressed_tasks_count_for_project_service(db: Session, project_id: int) -> int:
    """
    Return number of tasks in 'IN_PROGRESS' status for a given project.
    """
    try:
        if not get_project_by_id(db, project_id):
            raise GroundControlException(
                ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
            )

        count = (
            db.query(func.count(Task.id))
            .join(Step)
            .filter(Step.project_id == project_id, Task.status == Status.IN_PROGRESS)
            .scalar()
        )

        return count or 0

    except GroundControlException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve progressed task count for project %d: %s",
            project_id,
            e,
        )
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details="Unexpected error while retrieving task count",
        ) from e


def archive_project_service(db: Session, project_id: int):
    """
    Archive a project and all its related entities (steps, tasks, annotations).
    Sets all statuses to 'ARCHIVED' and preserves previous status where applicable.

    :param db: SQLAlchemy session object.
    :param project_id: ID of the project to archive.
    :raises GroundControlException: If project is not found or unexpected error occurs.
    :return: The archived project object.
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise GroundControlException(
                ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
            )

        if project.status == Status.DONE:
            logger.warning(
                "Project %d is DONE; cannot archive a finished project.", project_id
            )
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="archive",
                resource="project",
                id_part=f" with id {project_id} (already marked as DONE, cannot be archived)",
            )

        if project.status == Status.ARCHIVED:
            logger.warning("Project %d is already ARCHIVED", project_id)
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="archive",
                resource="project",
                id_part=f" with id {project_id} (already marked as ARCHIVED)",
            )

        logger.info("Archiving project %d...", project_id)

        # Archive project
        project.previous_status = project.status
        project.status = Status.ARCHIVED

        for step in project.steps:
            step.previous_status = step.status
            step.status = Status.ARCHIVED

            for task in step.tasks:
                task.previous_status = task.status
                task.status = Status.ARCHIVED

                for annotation in getattr(task, "annotations", []):
                    annotation.previous_status = annotation.annotation_status
                    annotation.annotation_status = Status.ARCHIVED

        db.commit()
        db.refresh(project)

        logger.info("Project %d archived successfully.", project_id)
        return project

    except GroundControlException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to archive project %d: %s", project_id, e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details=f"Unexpected error while archiving project {project_id}",
        ) from e


def unarchive_project_service(db: Session, project_id: int):
    """
    Unarchive a previously archived project and all its related entities.
    Reverts their statuses from 'ARCHIVED' back to the saved previous_status values.

    :param db: SQLAlchemy session object.
    :param project_id: ID of the project to restore.
    :raises GroundControlException: If project not found, not archived, or unexpected error occurs.
    :return: The restored project object.
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise GroundControlException(
                ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
            )

        if project.status != Status.ARCHIVED:
            logger.warning("Project %d is not archived; cannot restore.", project_id)
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="restore",
                resource="project",
                id_part=f" with id {project_id} (not archived)",
            )

        logger.info("Restoring archived project %d...", project_id)

        project.status = project.previous_status
        project.previous_status = None

        for step in project.steps:
            step.status = step.previous_status
            step.previous_status = None

            for task in step.tasks:
                task.status = task.previous_status
                task.previous_status = None

                for annotation in getattr(task, "annotations", []):
                    annotation.annotation_status = annotation.previous_status
                    annotation.previous_status = None

        db.commit()
        db.refresh(project)

        logger.info("Project %d restored successfully.", project_id)
        return project

    except GroundControlException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to restore project %d: %s", project_id, e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details=f"Unexpected error while restoring project {project_id}",
        ) from e
