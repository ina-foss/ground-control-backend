import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from src.database import Base, SessionLocal
from src.models.project_model import Project
from src.services.task_service import get_task_by_id, create_task_crud, update_data_task_crud
from src.schemas.task_schemas import TaskCreateDto

# Fixture to create an SQLite in-memory database for testing
# Create an in-memory SQLite database for testing
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_get_task_by_id(db_session: Session):
    # Create a task in the database
    task_data = {
        "name": "Test Task",
        "instruction": "Test instruction",
        "data": {"key": "value"},
        "project_id": 1
    }
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    # Retrieve the task by ID
    retrieved_task = get_task_by_id(db_session, created_task.id)

    # Assert that the retrieved task matches the created task
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == task_data["name"]
    assert retrieved_task.instruction == task_data["instruction"]
    assert retrieved_task.data == task_data["data"]
    assert retrieved_task.project_id == task_data["project_id"]

def test_create_task_crud(db_session: Session):
    # Create a task
    task_data = {
        "name": "Test Task",
        "instruction": "Test instruction",
        "data": {"key": "value"},
        "project_id": 1
    }
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    # Assert that the task is created successfully
    assert created_task is not None
    assert created_task.id is not None
    assert created_task.name == task_data["name"]
    assert created_task.instruction == task_data["instruction"]
    assert created_task.data == task_data["data"]
    assert created_task.project_id == task_data["project_id"]

def test_update_data_task_crud(db_session: Session):
    # Create a task
    task_data = {
        "name": "Test Task",
        "instruction": "Test instruction",
        "data": {"key": "value"},
        "project_id": 1
    }
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    # Update task data
    updated_data = {"new_key": "new_value"}
    updated_task = update_data_task_crud(created_task.id, updated_data, db_session)

    # Retrieve the updated task
    retrieved_updated_task = get_task_by_id(db_session, created_task.id)

    # Assert that the task data is updated successfully
    assert retrieved_updated_task is not None
    assert retrieved_updated_task.data == updated_data
