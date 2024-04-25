from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func


class User(Base):
    __tablename__ = 'user'

    userid = Column(Integer, primary_key=True)
    email = Column(String)
    role = Column(String)
    created_at = Column(DateTime)

    projects = relationship("Project", back_populates="owner")

    # tasks = relationship("Task", secondary=UserTask.__table__, back_populates="users")
    # user_task = relationship("UserTask",backref="users")
