from typing import Any, Dict

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from src.models.task_model import Task
from src.schemas.task_schemas import TaskCreateDto


def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def create_task_crud(task: TaskCreateDto, db: Session):
    db_task = Task(**jsonable_encoder(task))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_data_task_crud(id: int, data: Dict[str, Any], db: Session):
    db_task = get_task_by_id(db, task_id=id)
    if db_task is not None:
        db_task.data = data
        db.commit()
        db.refresh(db_task)
    return db_task
