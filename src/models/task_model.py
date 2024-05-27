from src.database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    instruction = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    data = Column(JSON)
    project_id = Column(Integer, ForeignKey('project.id'))

    annotations = relationship("Annotation", backref="task")
    # predictions = relationship("Prediction", backref="task")
