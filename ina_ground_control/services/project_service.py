from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from ina_ground_control.models.project_model import Project
from ina_ground_control.schemas.project_schemas import ProjectBaseDto


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of projects from the database with optional pagination.

    Attributes:
        db (Session): The database session used for querying.
        skip (int): The number of records to skip for pagination. Default is 0.
        limit (int): The maximum number of records to return. Default is 100.

    Returns:
        List[Project]: A list of Project objects.
    """
    return db.query(Project).offset(skip).limit(limit).all()


def get_project_by_id(db: Session, project_id: int):
    """
    Retrieve a project by its ID, including its tasks.

    Attributes:
        db (Session): The database session used for querying.
        project_id (int): The unique identifier of the project to retrieve.

    Returns:
        Project: The Project object if found, otherwise None.
    """
    return db.query(Project).options(joinedload(Project.tasks)).filter(Project.id == project_id).first()


def create_project_crud(db: Session, project: ProjectBaseDto):
    """
    Create a new project in the database.

    Attributes:
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

    Attributes:
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

    Attributes:
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
