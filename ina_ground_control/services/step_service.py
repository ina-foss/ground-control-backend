"""
This module provides CRUD operations for steps.

It includes functions to retrieve a step by ID, create a new step, and update an existing step.
"""

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from ina_ground_control import logger
from ina_ground_control.constants.enums import Status
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.step_model import Step
from ina_ground_control.schemas.step_schemas import StepCreate, StepSummaryDto


def get_step_by_id(db: Session, step_id: int) -> Step:
    """
    Retrieve a step by its ID.

    Attributes:
        db (Session): The database session used for querying.
        step_id (int): The unique identifier of the step to retrieve.

    Returns:
        Step: The step object if found, otherwise None.
    """
    step = db.query(Step).filter(Step.id == step_id).first()
    if step is None:
        logger.error("Failed to retrieve step with id: %d", step_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Step", id=step_id
        )
    return step


def get_steps_by_project_id(db: Session, project_id: int) -> list[StepSummaryDto]:
    steps = (
        db.query(
            Step.id,
            Step.annotation_type,
        )
        .filter(Step.project_id == project_id)
        .all()
    )

    return [
        StepSummaryDto(
            id=step.id,
            annotation_type=step.annotation_type,
        )
        for step in steps
    ]


def create_step_crud(step: StepCreate, db: Session):
    """
    Create a new step in the database.

    Attributes:
        step (StepCreate): The step data transfer object containing step details.
        db (Session): The database session used for querying.

    Returns:
        Step: The newly created Step object.
    """
    db_step = Step(**step.model_dump())
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


def update_data_step_crud(step_id: int, step: StepCreate, db: Session):
    """
    Update the data of an existing step in the database.

    Attributes:
        step_id (int): The unique identifier of the step to update.
        step (StepCreate): A new url for the step.
        db (Session): The database session used for querying.

    Returns:
        Step: The updated Step object if the step exists, otherwise None.
    """
    db_step = get_step_by_id(db, step_id=step_id)
    for key, value in step.model_dump().items():
        setattr(db_step, key, value)
    db.commit()
    db.refresh(db_step)
    return db_step


def delete_step_crud(db: Session, step_id: int):
    """
    Delete a step from the database.

    Parameters:
    db (Session): The database session used for querying.
    step_id (int): The unique identifier of the step to delete.

    Returns:
    Step: The deleted Step object if the step exists, otherwise None.
    """
    db_step = get_step_by_id(db, step_id)
    db.delete(db_step)
    db.commit()
    return db_step


def get_steps(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of steps from the database with optional pagination.

    Parameters:
    db (Session): The database session used for querying.
    skip (int): The number of records to skip for pagination. Default is 0.
    limit (int): The maximum number of records to return. Default is 100.

    Returns:
    List[step]: A list of step objects.
    """
    return db.query(Step).offset(skip).limit(limit).all()


def finish_step_crud(db: Session, step: Step) -> Step:
    step.status = Status.DONE
    step.validated_at = func.now()
    step.updated_at = func.now()
    db.commit()
    db.refresh(step)
    return step


def update_step_status_crud(db: Session, step: Step, status: Status) -> Step:
    step.status = status
    step.updated_at = func.now()
    db.commit()
    db.refresh(step)
    return step
