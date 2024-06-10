from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from src.models.project_model import Project
from src.schemas.project_schemas import ProjectBaseDto


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).options(joinedload(Project.tasks)).filter(Project.id == project_id).first()


def create_project_crud(db: Session, project: ProjectBaseDto):
    db_project = Project(
        title=project.title, description=project.description, created_by=project.created_by)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project_crud(db: Session, project: ProjectBaseDto, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is not None:
        db_project.title = project.title
        db_project.description = project.description
        db_project.updated_at = datetime.now()
        db_project.created_by = project.created_by
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_project_crud(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is not None:
        db.delete(db_project)
        db.commit()
    return db_project
