"""
This module defines the API endpoints related to step management within
the application.
Includes routes for creating, retrieving, and updating steps.
Utilizes database sessions for CRUD operations and handles exceptions
appropriately.

Endpoints:
    /step/{step_id}: Retrieves a step by its ID.
    /step/: Creates a new step.
    /step/{step_id}: Updates an existing step by its ID.
    /step/{step_id}: Delete step
    /step/: Retrieves all step
Dependencies:
    - External services: None.
    - Internal utilities: Database session, step service for CRUD operations.

Configuration:
    - Database session configuration and step schemas are defined in the
    `src` module.
"""

from fastapi import APIRouter, Body, Depends, status
from fastapi_keycloak_middleware import (
    AuthorizationResult,
    CheckPermissions,
    MatchStrategy,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.step_model import Step
from ina_ground_control.schemas.step_schemas import StepCreate, StepDto, StepSummaryDto
from ina_ground_control.services.step_service import (
    create_step_crud,
    delete_step_crud,
    get_step_by_id,
    get_steps,
    get_steps_by_project_id,
    update_data_step_crud,
    update_step_settings_crud,
)

router = APIRouter(tags=["step"])


# get step by id
@router.get("/step/{step_id}", response_model=StepDto)
def read_step(step_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a step by its unique identifier.

    Args:
        step_id (int): The unique identifier of the step.

    Returns:
        StepDto: The requested step's details.
    Raises:
        HTTPException: If the step is not found.
    """
    step = get_step_by_id(db, step_id=step_id)
    if step is None:
        logger.error("Failed to retrieve step with id: %d", step_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Step", id=step_id
        )
    return step


# add new step
@router.post("/step", response_model=StepCreate)
def create_step(step: StepCreate, db: Session = Depends(get_db)):
    """
    Create a new step.

    Args:
        step (StepCreate): The step data to be created.

    Returns:
        StepCreate: The newly created step's details.
    """
    try:
        return create_step_crud(step, db)
    except Exception as e:
        logger.error("Failed to create step: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Failed to create step"
        ) from e


# update step by id
@router.patch("/step/{step_id}", response_model=StepDto)
def update_data_step(step_id: int, step: StepCreate, db: Session = Depends(get_db)):
    """
    Update an existing step by its unique identifier.

    Args:
        step_id (int): The unique identifier of the step to update.
        step (StepCreate): The updated step's value.

    Returns:
        StepDto: The updated step's details.
    Raises:
        HTTPException: If the step is not found.
    """
    updated_step = update_data_step_crud(step_id, step, db)
    if updated_step is None:
        logger.error("Failed to update step with id: %d", step_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Step", id=step_id
        )
    return updated_step


# update the type-specific settings of a step
@router.put("/step/{step_id}/settings", response_model=StepDto)
def update_step_settings(
    step_id: int,
    settings: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Update the settings of a step according to its type.

    The step type determines which settings schema is used to validate the
    payload and to complete the missing values with the defaults.

    Args:
        step_id (int): The unique identifier of the step to update.
        settings (dict): The (possibly partial) settings payload.

    Returns:
        StepDto: The updated step, including its full settings.
    Raises:
        GroundControlException: If the step is not found or the settings are
            incompatible with the step type.
    """
    try:
        return update_step_settings_crud(db, step_id, settings)
    except ValidationError as e:
        logger.error("Invalid settings for step %d: %s", step_id, e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details=f"Invalid settings for step type: {e}",
        ) from e


# delete step
@router.delete(
    "/step/{step_id}", status_code=status.HTTP_200_OK, response_model=StepCreate
)
def delete_step(
    step_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.DELETE_STEP.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
):
    deleted_step = delete_step_crud(db, step_id)
    if deleted_step is None:
        logger.error("Failed to delete step with id: %d", step_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Step", id=step_id
        )
    return deleted_step


# get list of step
@router.get("/steps", response_model=list[StepDto])
def read_steps(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[Step]:
    """Retrieve a list of steps with pagination support."""
    steps = get_steps(db, skip=skip, limit=limit)
    return steps


@router.get(
    "/projects/{project_id}/steps",
    response_model=list[StepSummaryDto],
)
def read_project_steps(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[StepSummaryDto]:
    return get_steps_by_project_id(db, project_id)
