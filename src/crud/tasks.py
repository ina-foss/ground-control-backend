from sqlalchemy.orm import Session

from src.models.tasks_model import *

def get_task_by_id(db: Session, taskid: int ):
    return db.query(Task).filter(Task.taskid == taskid).first()
