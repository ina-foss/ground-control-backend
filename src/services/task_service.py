from sqlalchemy.orm import Session

from src.models.tasks_model import *
from src.schemas.task_schemas import TaskCreateDto

def get_task_by_id(db: Session, task_id: int ):
    return db.query(Task).filter(Task.id == task_id).first()

def create_task_crud(task: TaskCreateDto, db: Session):
    db_task = Task(name=task.name, project_id = task.project_id, data=task.data, instruction=task.instruction)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
