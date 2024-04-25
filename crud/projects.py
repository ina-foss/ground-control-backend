from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models.project_model import *
from schemas.project_schemas import *

def get_projects(db: Session, skip: int=0, limit: int= 100):
    return db.query(Project).offset(skip).limit(limit).all()

def get_project_by_id(db: Session, projectid: int):
    return db.query(Project).options(joinedload(Project.tasks)).filter(Project.projectid == projectid).first()

def create_project_crud(db: Session, project: ProjectBase):
    db_project= Project(title=project.title, description= project.description, created_by= project.created_by)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_crud(db: Session, project: ProjectBase, projectid: int):
    db_project = db.query(Project).filter(Project.projectid == projectid).first()
    if(db_project is not None):
        db_project.title = project.title
        db_project.description = project.description
        db_project.updated_at = datetime.now()
        db.commit()
        db.refresh(db_project)
    return db_project