from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models.tasks_model import *

def get_task_by_id(db: Session, taskid: int ):
    return db.query(Task).filter(Task.taskid == taskid).first()