from sqlalchemy.orm import Session

from src.models.tasks_model import *

def get_task_by_id(db: Session, task_id: int ):
    return db.query(Task).filter(Task.id == task_id).first()
