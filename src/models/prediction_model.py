"""
This module defines the Prediction model for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.sql.expression import func
from src.database import Base


class Prediction(Base):
    """
    Represents a prediction record in the database.

    Attributes:
        id (Integer): The unique identifier of the prediction.
        model_name (String): The name of the model used for the prediction.
        model_version (String): The version of the model used for the prediction.
        result (JSON): The result of the prediction stored as JSON.
        score (Float): The confidence score of the prediction.
        created_at (DateTime): The timestamp when the prediction was created.
        updated_at (DateTime): The timestamp when the prediction was last updated.
        task_id (Integer): The foreign key linking to the task associated with the prediction.
        project_id (Integer): The foreign key linking to the project associated with the prediction.
    """

    __tablename__ = 'prediction'

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    model_version = Column(String)
    result = Column(JSON)
    score = Column(Float)
    created_at = Column(DateTime, default=func.now())  # Corrected usage
    updated_at = Column(DateTime)
    task_id = Column(Integer, ForeignKey('task.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
