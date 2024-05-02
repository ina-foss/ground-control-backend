from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db

from src.schemas.project_schemas import *
from src.services.project_service import *
router = APIRouter(tags=["project"])


@router.get("/projects/", response_model=list[ProjectDetailDto])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = get_projects(db, skip=skip, limit=limit)
    return projects

@router.post("/project/", response_model=ProjectDetailDto)
def create_project(
        project: ProjectBaseDto, db:Session = Depends(get_db)
):
    return create_project_crud(db, project)

@router.get("/project/{project_id}", response_model=ProjectListDto,response_model_by_alias=False)
def read_project(project_id:int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id = project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/project/{project_id}", response_model=ProjectWithIdDto)
def update_project(
        project_id: int,
        project: ProjectBaseDto,
        db: Session = Depends(get_db)
):
    updated_project = update_project_crud(db, project, project_id)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/project/{project_id}", response_model=ProjectWithIdDto)
def delete_project(
        project_id: int,
        db: Session = Depends(get_db)
):
    deleted_project = delete_project_crud(db, project_id)
    if deleted_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted_project
