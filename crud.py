from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

import models,schemas

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_projects(db: Session, skip: int=0, limit: int= 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def get_project_by_id(db: Session, projectid: int):
    return db.query(models.Project).options(joinedload(models.Project.tasks)).filter(models.Project.projectid == projectid).first()

# def get_users(db: Session, skip: int= 0, limit: int= 100):
#     return db.query(models.User).options(joinedload(models.User.tasks)).offset(skip).limit(limit).all()


def get_task_by_id(db: Session, taskid: int ):
    return db.query(models.Task).filter(models.Task.taskid == taskid).first()

def create_project(db: Session, project: schemas.ProjectBase):
    db_project= models.Project(title=project.title, description= project.description, created_by= project.created_by)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project