import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.services.task_service import get_task_by_id, create_task_crud, update_data_task_crud
from ina_ground_control.schemas.task_schemas import TaskCreateDto

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


task_data = {
    "name": "Test Task",
    "instruction": "Test instruction",
    "data": {"key":"value"},
    "data_type" : "ldd",
    "status" : "draft",
    "lead_time" : 1,
    "step_id" : 1,
    "media_id" : 1,
}




def test_get_task_by_id(db_session: Session):

    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    retrieved_task = get_task_by_id(db_session, created_task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == task_data["name"]
    assert retrieved_task.instruction == task_data["instruction"]
    # assert retrieved_task.data == task_data["data"]
    assert retrieved_task.data_type.value == task_data["data_type"]
    assert retrieved_task.status.value == task_data["status"]
    assert retrieved_task.lead_time == task_data["lead_time"]
    assert retrieved_task.step_id == task_data["step_id"]
    assert retrieved_task.media_id == task_data["media_id"]



def test_create_task_crud(db_session: Session):

    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    assert created_task is not None
    assert created_task.id is not None
    assert created_task.name == task_data["name"]
    assert created_task.instruction == task_data["instruction"]
    # assert created_task.data == task_data["data"]
    assert created_task.data_type.value == task_data["data_type"]
    assert created_task.status.value == task_data["status"]
    assert created_task.lead_time == task_data["lead_time"]
    assert created_task.step_id == task_data["step_id"]
    assert created_task.media_id == task_data["media_id"]

def test_update_data_task_crud(db_session: Session):

    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    updated_data ={"key":"value updated"}

    update_data_task_crud(
        created_task.id, updated_data, db_session)

    retrieved_updated_task = get_task_by_id(db_session, created_task.id)

    assert retrieved_updated_task is not None
    assert retrieved_updated_task.data == updated_data
