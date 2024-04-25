from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from typing import Dict, Any, ForwardRef


    
class UserTask(BaseModel):
    user_taskId: int
    userId: int
    taskId: int
    task_status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Prediction(BaseModel):
    predictionid: int
    model_name: Optional[str]
    model_version: Optional[str]
    result: Optional[Dict[str, Any]]
    score: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    taskid: int
    projectid: int
    




class TaskBase(BaseModel):
    taskid: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    projectid: int


    class Config:
        orm_mode = True
        


class UserBase(BaseModel):
    userid: int
    email: EmailStr
    role: str
    created_at: Optional[datetime]


    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    title: Optional[str]
    description: Optional[str]
    created_by: int

    class Config:
            orm_mode: True
        

class Project(ProjectBase):
    projectid: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tasks: list[TaskBase] = []  
    total_tasks: int  

    class Config:
        orm_mode: True


class Annotation(BaseModel):
    annotationid: int
    userid: int
    result: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    validated_at: Optional[datetime]
    taskid: int
    projectid: int
    status: str
    user: UserBase

    class Config:
        orm_mode: True



class User(UserBase):

    projects: list[Project]= []

    class Config:
        orm_mode: True

class UserTask(BaseModel):
    attributed_at: Optional[datetime]
    validated_at: Optional[datetime]
    task_status: str

class UserWithUserwithTask(UserBase):
    task_progress: list[UserTask] = Field(...,alias="user_task")

class TaskList(TaskBase):  
    name: Optional[str]
    instruction: Optional[str]
    annotations: list[Annotation] = []
    predictions: list[Prediction] = []
    


class TaskDetail(TaskList):
    data: Optional[Dict[str, Any]]= []



class UserWithTasks(User):
    tasks: list[TaskList] = []



class ProjectList(ProjectBase):
    tasks: list[TaskList] = []

