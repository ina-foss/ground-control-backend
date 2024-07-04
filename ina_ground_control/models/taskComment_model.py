from ina_ground_control.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class TaskComment(Base):
    __tablename__ = "taskComment"

    id = Column(Integer, primary_key=True)
    comment = Column(String)
    task_id = Column(Integer, ForeignKey("task.id"))

