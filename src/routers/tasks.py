from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db

from src.schemas.task_schemas import TaskDetailDto
from src.services.task_service import get_task_by_id

router = APIRouter(tags=["task"])


@router.get("/task/{id}",response_model= TaskDetailDto)
def read_task(id:int, db:Session = Depends(get_db)):
    task = get_task_by_id(db, task_id = id)
    if task is None:
        raise HTTPException(status_code=404, detail= "Task not found")
    return task
