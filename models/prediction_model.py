from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func

class Prediction(Base):
    __tablename__ = 'prediction'

    predictionid = Column(Integer, primary_key=True)
    model_name = Column(String)
    model_version = Column(String)
    result = Column(JSON)
    score = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    taskid = Column(Integer, ForeignKey('task.taskid'))
    projectid = Column(Integer, ForeignKey('project.projectid'))
