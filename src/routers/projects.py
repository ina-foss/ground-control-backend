from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter(tags=["project"])


@router.get("/projects/", response_model=list[ProjectDetail])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = get_projects(db, skip=skip, limit=limit)
    return projects

@router.post("/project/", response_model=ProjectDetail)
def create_project(
    project: ProjectBase, db:Session = Depends(get_db)
):
    return create_project_crud(db, project)

@router.get("/project/{projectid}", response_model=ProjectList,response_model_by_alias=False)
def read_project(projectid:int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, projectid = projectid)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/project/{projectid}", response_model=ProjectDetail)
def update_project(
    projectid: int, 
    project: ProjectBase, 
    db: Session = Depends(get_db)
):
    updated_project = update_project_crud(db, project, projectid)
    if updated_project is None:
          raise HTTPException(status_code=404, detail="Project not found")
    return updated_project
