from sqlalchemy import Column, Enum, ForeignKey, Integer
from enum import Enum as PyEnum
from ina_ground_control.database import Base

class InOutEnum(PyEnum):
    """
    Enum representing the two types of relation between Task and Annotation

    Attributes
    ----------
        IN (str): The annotation is the initial data of task, can either come from an algorithm or an annotation form previous step.
        OUT (str): The annotation is the result of the task, contains the user work.
    """

    IN = "in"
    OUT = "out"

class Annotation_Task(Base):
    """
    Describe a relation between an annotation object and a task object

    Attributes:
        annotation_id (Integer): Identifier of the annotation object
        task_id (Integer): Identifier of the task object
        direction (enumerate): Describe the 'direction' of the relation.
    """
    __tablename__ = "annotation_task"

    annotation_id = Column(Integer, ForeignKey("annotation.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    direction = Column(Enum(InOutEnum), nullable=False)


