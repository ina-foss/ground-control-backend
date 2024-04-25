from src.database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func

from .tasks_model import Task

from .user_model import User


class Project(Base):
    __tablename__ = 'project'

    projectid = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.sysdate())
    updated_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey('user.userid'))

    owner = relationship("User",back_populates="projects")

    tasks = relationship('Task', backref="projects")

    total_tasks = column_property(
        select(func.count()).where(Task.projectid == projectid).correlate_except(Task).scalar_subquery()
    )
