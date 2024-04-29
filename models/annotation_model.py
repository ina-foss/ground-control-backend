from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func

class Annotation(Base):
    __tablename__ = 'annotation'

    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('user.id'))
    result = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    validated_at = Column(DateTime)
    taskid = Column(Integer, ForeignKey('task.id'))
    projectid = Column(Integer, ForeignKey('project.id'))
    status = Column(String)

    user = relationship("User", backref="annotations")