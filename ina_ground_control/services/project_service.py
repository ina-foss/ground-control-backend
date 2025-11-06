"""
Service related to project objects.

Functions:
- get_projects
- get_project_by_id
- create_project_crud
- update_project_crud
- delete_project_crud
"""

from datetime import datetime

from fastapi import Request
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ina_ground_control import logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_model import AnnotationStatus
from ina_ground_control.models.project_model import Project, ProjectStatus
from ina_ground_control.models.step_model import Step, StepStatus
from ina_ground_control.models.task_model import Task, TaskStatus
from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.schemas.task_schemas import TaskWithIdDto


def get_relevant_task_for_user(project, user_email: str, roles: list[str]):
    """
    Given a project and a user, return the first relevant task to annotate
    according to user role and annotation logic.
    """
    if Permission.ADMIN_PROJECT.value in roles:
        return project

    now = datetime.utcnow()
    all_filtered_tasks = []
    for step in project.steps:
        for task in step.tasks:
            # Condition 1: tasks in progress by this user
            if any(
                ann.user_email == user_email
                and ann.annotation_status == AnnotationStatus.IN_PROGRESS
                for ann in task.annotations
            ):
                all_filtered_tasks.append(task)
                # TODO: => continue
                break

            # Condition 2: insufficient redundancy or expired pending
            other_anns_in_progress = [
                ann
                for ann in task.annotations
                if ann.annotation_status == AnnotationStatus.IN_PROGRESS
                and ann.user_email != user_email
            ]
            if (
                task.status == TaskStatus.IN_PROGRESS
                and len(other_anns_in_progress) < task.redundancy
            ):
                all_filtered_tasks.append(task)
                # TODO: => continue
                break

            # Condition 3: pending tasks and prioritize expired pending
            if task.status == TaskStatus.PENDING:
                if task.expiration_date and task.expiration_date <= now:
                    all_filtered_tasks.insert(0, task)
                else:
                    all_filtered_tasks.append(task)
    # TODO:
    # In the future, we may use `step.max_tasks_per_person` (or a project-level limit)
    # to determine how many tasks to assign per user for a given project.
    # For now, we only return the first relevant task available for the user.
    if all_filtered_tasks:
        project.tasks_to_annotate = [all_filtered_tasks[0]]
    else:
        project.tasks_to_annotate = None
    return project


def get_projects(db: Session, request: Request, skip: int = 0, limit: int = 100):
    projects = db.query(Project).offset(skip).limit(limit).all()
    current_user = request.scope.get("user", {})
    roles = current_user.roles
    user_email = current_user.email

    for project in projects:
        get_relevant_task_for_user(project, user_email, roles)
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
    roles = current_user.roles

    project = get_relevant_task_for_user(project, user_email, roles)
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


def update_project_status_crud(db: Session, project_id: int, status: ProjectStatus):
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
    if project.status == ProjectStatus.DONE:
        logger.warning("Project %d is already DONE", project_id)
        raise GroundControlException(
            ErrorCode.BAD_REQUEST,
            action="finish",
            resource="project",
            id_part=f" with id {project_id} (already marked as DONE)",
        )
    project.status = ProjectStatus.DONE
    project.updated_at = func.now()
    for step in project.steps:
        step.status = StepStatus.DONE
        step.updated_at = func.now()
        for task in step.tasks:
            task.status = TaskStatus.DONE
            task.updated_at = func.now()
            for annotation in getattr(task, "annotations", []):
                annotation.annotation_status = AnnotationStatus.DONE
                annotation.updated_at = func.now()
    db.commit()
    db.refresh(project)
    return project


def get_progressed_tasks_for_project_service(
    db: Session, project_id: int
) -> list[TaskWithIdDto]:
    """
    Return all tasks in 'IN_PROGRESS' status for a given project.
    """
    try:
        project_exists = get_project_by_id(db, project_id)
        if not project_exists:
            logger.error("Project with id %d not found", project_id)
            raise GroundControlException(
                ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
            )

        tasks = (
            db.query(Task)
            .join(Step)
            .join(Project)
            .filter(Project.id == project_id, Task.status == TaskStatus.IN_PROGRESS)
            .all()
        )

        validated_tasks = [
            TaskWithIdDto.model_validate(task, from_attributes=True) for task in tasks
        ]

        return validated_tasks

    except GroundControlException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve in-progress tasks for project %d: %s", project_id, e
        )
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details=f"Unexpected error while retrieving in-progress tasks for project {project_id}",
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

        if project.status == ProjectStatus.DONE:
            logger.warning(
                "Project %d is DONE; cannot archive a finished project.", project_id
            )
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="archive",
                resource="project",
                id_part=f" with id {project_id} (already marked as DONE, cannot be archived)",
            )

        if project.status == ProjectStatus.ARCHIVED:
            logger.warning("Project %d is already ARCHIVED", project_id)
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="archive",
                resource="project",
                id_part=f" with id {project_id} (already marked as ARCHIVED)",
            )

        logger.info("Archiving project %d...", project_id)

        # Archive project
        project.archived_status = project.status
        project.status = ProjectStatus.ARCHIVED

        for step in project.steps:
            step.archived_status = step.status
            step.status = StepStatus.ARCHIVED

            for task in step.tasks:
                task.archived_status = task.status
                task.status = TaskStatus.ARCHIVED

                for annotation in getattr(task, "annotations", []):
                    annotation.archived_status = annotation.annotation_status
                    annotation.annotation_status = AnnotationStatus.ARCHIVED

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
    Reverts their statuses from 'ARCHIVED' back to the saved archived_status values.

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

        if project.status != ProjectStatus.ARCHIVED:
            logger.warning("Project %d is not archived; cannot restore.", project_id)
            raise GroundControlException(
                ErrorCode.BAD_REQUEST,
                action="restore",
                resource="project",
                id_part=f" with id {project_id} (not archived)",
            )

        logger.info("Restoring archived project %d...", project_id)

        project.status = project.archived_status
        project.archived_status = None

        for step in project.steps:
            step.status = step.archived_status
            step.archived_status = None

            for task in step.tasks:
                task.status = task.archived_status
                task.archived_status = None

                for annotation in getattr(task, "annotations", []):
                    annotation.annotation_status = annotation.archived_status
                    annotation.archived_status = None

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
