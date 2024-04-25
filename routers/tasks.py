from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from schemas.task_schemas import TaskDetail
from crud.tasks import get_task_by_id

router = APIRouter(tags=["task"])


@router.get("/task/{id}",response_model= TaskDetail)
def read_task(id:int, db:Session = Depends(get_db)):
    task = get_task_by_id(db, taskid = id)
    if task is None:
        raise HTTPException(status_code=404, detail= "Task not found")
    return task


