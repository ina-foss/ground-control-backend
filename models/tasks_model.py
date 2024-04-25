from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func

from .annotation_model import Annotation
from .prediction_model import Prediction

class Task(Base):
    __tablename__ = 'task'

    taskid = Column(Integer, primary_key=True)
    name = Column(String)
    instruction = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    data = Column(JSON)
    projectid = Column(Integer, ForeignKey('project.projectid'))
    # users = relationship("User", secondary=UserTask.__table__, back_populates="tasks")
    # user_task= relationship("UserTask",backref="tasks")


    annotations = relationship("Annotation", backref="Task" )
    predictions = relationship("Prediction", backref="Task")