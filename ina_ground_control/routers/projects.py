"""
This module contains the implementation of CRUD for managing projects within the application.
It provides FastAPI route handlers for creating, reading, updating, and deleting projects.
Projects are represented through DTOs (Data Transfer Objects) defined in `project_schemas.py`,
 and business logic is implemented in `project_service.py`.

Key Features:
    - Pagination support for listing projects.
    - Detailed project information retrieval by ID.
    - Creation of new projects with validation.
    - Update of existing projects with partial updates supported.
    - Deletion of projects by ID.

Dependencies:
    - Database session management via `get_db` from `src.database`.
    - Project-related schemas from `src.schemas.project_schemas`.
    - Business logic for project operations in `src.services.project_service`.
"""

import time

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi_keycloak_middleware import (
    AuthorizationResult,
    CheckPermissions,
    MatchStrategy,
)
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.project_model import Project
from ina_ground_control.schemas.project_schemas import (
    ProjectBaseDto,
    ProjectDetailDto,
    ProjectListDto,
    ProjectListDtoSummary,
    ProjectParametersResponse,
    ProjectWithIdDto,
)
from ina_ground_control.services.project_service import (
    archive_project_service,
    create_project_crud,
    delete_project_crud,
    finish_project_service,
    get_progressed_tasks_count_for_project_service,
    get_project_by_id,
    get_project_by_id_based_on_user_role,
    get_project_parameters,
    get_projects,
    get_projects_count,
    get_projects_summary,
    unarchive_project_service,
    update_project_crud,
)

router = APIRouter(tags=["project"])


@router.get(
    "/projects",
    response_model=list[ProjectListDto],
)
def read_projects(
    response: Response,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Project]:
    """Retrieve a list of projects with pagination support."""
    # Get total count efficiently with a single COUNT query
    total_count = get_projects_count(db)

    # Get paginated projects
    projects = get_projects(db, request, skip=skip, limit=limit)

    response.headers["X-Total-Count"] = str(total_count)
    return projects


@router.get(
    "/projects/summary",
    response_model=list[ProjectListDtoSummary],
)
def read_projects_summary(
    response: Response,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ProjectListDtoSummary]:
    """Retrieve a list of projects with pagination support (optimized)."""
    start_total = time.perf_counter()

    # Get total count efficiently with a single COUNT query
    start = time.perf_counter()
    total_count = get_projects_count(db)
    logger.info("get_projects_count took %.3fs", time.perf_counter() - start)

    # Get paginated projects with optimized query
    start = time.perf_counter()
    summaries = get_projects_summary(db, request, skip=skip, limit=limit)
    logger.info("get_projects_summary took %.3fs", time.perf_counter() - start)

    response.headers["X-Total-Count"] = str(total_count)

    start = time.perf_counter()
    result = [ProjectListDtoSummary(**summary) for summary in summaries]
    logger.info("Building response took %.3fs", time.perf_counter() - start)
    logger.info(
        "Total read_projects_summary took %.3fs", time.perf_counter() - start_total
    )

    return result


@router.post("/project", response_model=ProjectDetailDto)
def create_project(
    project: ProjectBaseDto,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.CREATE_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
) -> ProjectDetailDto:
    """Create a new project."""
    try:
        return create_project_crud(db, project)
    except Exception as e:
        logger.error("Failed to create project: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Failed to create project"
        ) from e


@router.get(
    "/project/{project_id}/basic",
    response_model=ProjectListDto,
    response_model_by_alias=False,
)
def read_project_basic(project_id: int, db: Session = Depends(get_db)) -> Project:
    """Get a project without user-based filtering."""
    project = get_project_by_id(db, project_id=project_id)
    return project


@router.get(
    "/project/{project_id}",
    response_model=ProjectListDto,
    response_model_by_alias=False,
)
def read_project(
    project_id: int, request: Request, db: Session = Depends(get_db)
) -> Project:
    """Get a project filtered according to the user's role."""
    project = get_project_by_id_based_on_user_role(db, request, project_id=project_id)
    return project


@router.put("/project/{project_id}", response_model=ProjectWithIdDto)
def update_project(
    project_id: int,
    project: ProjectBaseDto,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.UPDATE_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
) -> Project:
    """Update an existing project by ID."""
    updated_project = update_project_crud(db, project, project_id)
    if updated_project is None:
        logger.error("Failed to update project with id: %d", project_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
        )
    return updated_project


@router.delete(
    "/project/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectWithIdDto,
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.DELETE_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
):
    """Delete a project by ID."""
    deleted_project = delete_project_crud(db, project_id)
    if deleted_project is None:
        logger.error("Failed to delete project with id: %d", project_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
        )
    return deleted_project


@router.get("/{project_id}/parameters", response_model=ProjectParametersResponse)
def read_project_parameters(project_id: int, db: Session = Depends(get_db)):
    parameters = get_project_parameters(db, project_id)
    if parameters is None:
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Project", id=project_id
        )
    return parameters


@router.post("/{project_id}/finish", response_model=ProjectWithIdDto)
def finish_project(
    project_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.FINISH_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name):
):
    project = finish_project_service(db, project_id)
    return project


@router.post("/{project_id}/progressed_tasks/count", response_model=int)
def get_progressed_tasks_count_for_project(
    project_id: int, db: Session = Depends(get_db)
):
    return get_progressed_tasks_count_for_project_service(db, project_id)


@router.post("/{project_id}/archive", response_model=ProjectWithIdDto)
def archive_project(
    project_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.ARCHIVE_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name):
):
    project = archive_project_service(db, project_id)
    return project


@router.post("/{project_id}/unarchive", response_model=ProjectWithIdDto)
def unarchive_project(
    project_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.UNARCHIVE_PROJECT.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name):
):
    project = unarchive_project_service(db, project_id)
    return project
