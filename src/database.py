"""
This module sets up the SQLAlchemy engine and session factory for our application.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv('.env.local')

PG_SERVER = os.getenv('PG_SERVER')
PG_DATABASE = os.getenv('PG_DATABASE')
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')

DATABASE_URL = f'{PG_SERVER}://{PG_USERNAME}:{PG_PASSWORD}@db:{PG_PORT}/{PG_DATABASE}'
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# from src.models.project_model import Project, ProjectStatus, AnnotationType
# from src.models.task_model import Task
# from src.models.user_model import User
# from src.models.prediction_model import Prediction
# from src.models.annotation_model import Annotation
def get_db():
    """
    Get a new database session and close it after use.

    Yields:
        Session: A SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
