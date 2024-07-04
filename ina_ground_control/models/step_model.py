
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from ina_ground_control.database import Base
from enum import Enum as PyEnum


class ProjectStatus(PyEnum):
    """
    Enum representing the different statuses a project can have.

    Attributes:
        DRAFT (str): The project is in draft status.
        PENDING (str): The project is pending and awaiting further actions.
        ENDED (str): The project has ended.
    """
    DRAFT = "draft"
    PENDING = "pending"
    ENDED = "ended"


class AnnotationType(PyEnum):
    """
    Enum representing the different types of annotations.

    Attributes:
        SEGMENTATION (str): The annotation type for segmentation tasks.
        TRANSCRIPTION (str): The annotation type for transcription tasks.
    """
    SEGMENTATION = "segmentation"
    TRANSCRIPTION = "transcription"


class Step(Base):
    __tablename__ = "step"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(ProjectStatus), nullable=False)
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    pinned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))
    tasks = relationship("Task", backref="step", cascade="all, delete-orphan")




