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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_keycloak_middleware import (
    MatchStrategy,
    CheckPermissions,
    AuthorizationResult
)
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.models.project_model import Project
from ina_ground_control.schemas.project_schemas import (ProjectBaseDto,
                                                        ProjectDetailDto,
                                                        ProjectListDto,
                                                        ProjectWithIdDto)
from ina_ground_control.services.project_service import (get_projects,
                                                         create_project_crud,
                                                         get_project_by_id,
                                                         update_project_crud,
                                                         delete_project_crud)
from ina_ground_control.constants.roles import Permission

logger = get_logger()
router = APIRouter(tags=["project"])
NOT_FOUND_STR = "Project not found"


@router.get("/projects", response_model=list[ProjectDetailDto])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[Project]:
    """Retrieve a list of projects with pagination support."""
    projects = get_projects(db, skip=skip, limit=limit)
    return projects


@router.post("/project", response_model=ProjectDetailDto)
def create_project(project: ProjectBaseDto,
                   db: Session = Depends(get_db),
                   _authorization_result: AuthorizationResult = Depends(
                       CheckPermissions( [Permission.CREATE_PROJECT.value],
                       match_strategy=MatchStrategy.AND))
                   # pylint: disable=invalid-name
                   ) -> ProjectDetailDto:
    """Create a new project."""
    try:
        return create_project_crud(db, project)
    except Exception as e:
        logger.error("Failed to create project: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create project") from e

@router.get("/project/{project_id}", response_model=ProjectListDto, response_model_by_alias=False)
def read_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    """Get details of a single project by ID."""
    project = get_project_by_id(db, project_id=project_id)
    if project is None:
        logger.error("Failed to retrieve project with id: %d", project_id)
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR)
    return project


@router.put("/project/{project_id}", response_model=ProjectWithIdDto)
def update_project(project_id: int, project: ProjectBaseDto, db: Session = Depends(get_db)) \
        -> Project:
    """Update an existing project by ID."""
    updated_project = update_project_crud(db, project, project_id)
    if updated_project is None:
        logger.error("Failed to update project with id: %d", project_id)
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR)
    return updated_project

@router.delete("/project/{project_id}", status_code=status.HTTP_200_OK,response_model=ProjectWithIdDto)
def delete_project(project_id: int, db: Session = Depends(get_db),_authorization_result: AuthorizationResult = Depends(
    CheckPermissions([Permission.DELETE_PROJECT.value],
                     match_strategy=MatchStrategy.AND))
                   # pylint: disable=invalid-name
                   ):
    """Delete a project by ID."""
    deleted_project = delete_project_crud(db, project_id)
    if deleted_project is None:
        logger.error("Failed to delete project with id: %d", project_id)
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR)
    return deleted_project
