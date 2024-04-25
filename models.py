from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.sql import select, func

from sqlalchemy.ext.hybrid import hybrid_property


class UserTask(Base):
    __tablename__ = 'user_task'

    userid = Column(Integer, ForeignKey('user.userid'),primary_key=True )
    task_status = Column(String)
    taskid = Column(Integer, ForeignKey('task.taskid'),primary_key=True )
    attributed_at = Column(DateTime)
    validated_at = Column(DateTime)

   

class User(Base):
    __tablename__ = 'user'

    userid = Column(Integer, primary_key=True)
    email = Column(String)
    role = Column(String)
    created_at = Column(DateTime)

    projects = relationship("Project", back_populates="owner")

    tasks = relationship("Task", secondary=UserTask.__table__, back_populates="users")
    user_task = relationship("UserTask",backref="users")


class Task(Base):
    __tablename__ = 'task'

    taskid = Column(Integer, primary_key=True)
    name = Column(String)
    instruction = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    data = Column(JSON)
    projectid = Column(Integer, ForeignKey('project.projectid'))
    users = relationship("User", secondary=UserTask.__table__, back_populates="tasks")
    user_task= relationship("UserTask",backref="tasks")


    annotations = relationship("Annotation", backref="Task" )
    predictions = relationship("Prediction", backref="Task")

class Project(Base):
    __tablename__ = 'project'

    projectid = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey('user.userid'))

    owner = relationship("User",back_populates="projects")

    tasks = relationship('Task', backref="projects")

    total_tasks = column_property(
        select(func.count()).where(Task.projectid == projectid).correlate_except(Task).scalar_subquery()
    )



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

class Annotation(Base):
    __tablename__ = 'annotation'

    annotationid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('user.userid'))
    result = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    validated_at = Column(DateTime)
    taskid = Column(Integer, ForeignKey('task.taskid'))
    projectid = Column(Integer, ForeignKey('project.projectid'))
    status = Column(String)

    user = relationship("User", backref="annotations")

    
