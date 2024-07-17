"""
This module provides CRUD operations for steps.

It includes functions to retrieve a step by ID, create a new step, and update an existing step.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.step_model import Step
from ina_ground_control.schemas.step_schemas import StepCreate


def get_step_by_id(db: Session, step_id: int):
    """
    Retrieve a step by its ID.

    Attributes:
        db (Session): The database session used for querying.
        step_id (int): The unique identifier of the step to retrieve.

    Returns:
        Step: The step object if found, otherwise None.
    """
    return db.query(Step).filter(Step.id == step_id).first()

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

def update_data_step_crud(step_id: int, step: StepCreate, db: Session ):
    """
    Update the data of an existing media in the database.

    Attributes:
        step_id (int): The unique identifier of the step to update.
        step (StepCreate): A new url for the step.
        db (Session): The database session used for querying.

    Returns:
        Step: The updated Step object if the step exists, otherwise None.
    """
    db_media = get_step_by_id(db, step_id=step_id)
    if db_media is not None:
        for key, value in step.model_dump().items():
            setattr(db_media, key, value)
        db.commit()
        db.refresh(db_media)
    return db_media

def delete_step_crud(db: Session, step_id: int):
    """
    Delete a step from the database.

    Parameters:
    db (Session): The database session used for querying.
    step_id (int): The unique identifier of the step to delete.

    Returns:
    Step: The deleted Step object if the step exists, otherwise None.
    """
    db_step = db.query(Step).filter(Step.id == step_id).first()
    if db_step is not None:
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