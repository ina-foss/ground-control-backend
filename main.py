
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from routers import projects,tasks,users

from database import get_db

import crud, models, schemas
from database import SessionLocal, engine

app = FastAPI()

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)

origins = [
    "http://localhost:3000",
    "https://localhost:3000",

    "http://frontend:3000",
    "https://frontend:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Hello World"}

# @app.get("/users/", response_model=list[schemas.User],response_model_by_alias=False)
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/projects/", response_model=list[schemas.Project])
# def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     projects = crud.get_projects(db, skip=skip, limit=limit)
#     return projects

# @app.get("/project/{projectid}", response_model=schemas.ProjectList,response_model_by_alias=False)
# def read_project(projectid:int, db: Session = Depends(get_db)):
#     project = crud.get_project_by_id(db, projectid = projectid)
#     if project is None:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return project

# @app.get("/task/{id}",response_model= schemas.TaskDetail)
# def read_task(id:int, db:Session = Depends(get_db)):
#     task = crud.get_task_by_id(db, taskid = id)
#     if task is None:
#         raise HTTPException(status_code=404, detail= "Task not found")
#     return task

# @app.post("/project/", response_model=schemas.ProjectBase)
# def create_project(
#     project: schemas.ProjectBase, db:Session = Depends(get_db)
# ):
#     return crud.create_project(db, project)