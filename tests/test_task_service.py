from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.services.annotation_service import create_annotation_crud, finish_annotation_crud, skip_annotation_crud
from ina_ground_control.services.project_service import create_project_crud
from ina_ground_control.services.step_service import create_step_crud, update_data_step_crud
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.database import Base
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate, AnnotationStatus
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.schemas.task_schemas import TaskCreateDto, TaskStatus
from ina_ground_control.services.task_service import finish_task, get_task_by_id, create_task_crud, undone_task, update_data_task_crud, \
    delete_task_crud, update_task_status_crud


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

project_data = {
    "title": "Test Project 1",
    "description": "Test description 2",
    "status": "draft",
    "annotation_type": "segmentation",
    "is_published": True,
    "allow_skip": True,
    "control_weights": 10,
    "empty_annotations": True,
    "pinned_at": "2022-12-27 08:26:49.219717",
    "created_by": "john@example.com",
}

task_data = {
    "name": "Test Task",
    "instruction": "Test instruction",
    "data": {"key": "value"},
    "data_type": "ldd",
    "status": TaskStatus.DRAFT,
    "redundancy": 1,
    "lead_time": 1,
    "step_id": 1,
    "media_id": 1,
}

step_data_1 = {
    "title": "step 1",
    "description": "la premiere step",
    "annotation_type": "segmentation",
    "status": "draft",
    "pinned_at": "2022-12-27 08:26:49.219717",
    "project_id": 1,
    "allow_empty_annotation": True
}


annotation_data = {
    "annotation": {
        "user_email": "user.email@ina.fr",
"annotation_status": AnnotationStatus.IN_PROGRESS,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 1,  # Ensure unique annotation IDs
        "task_id": 1,
        "direction": InOutEnum.OUT
    }
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
    assert retrieved_task.status == task_data["status"]
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
    assert created_task.status == task_data["status"]
    assert created_task.lead_time == task_data["lead_time"]
    assert created_task.step_id == task_data["step_id"]
    assert created_task.media_id == task_data["media_id"]

def test_finish_task_crud(db_session: Session):
    
    create_project_crud(db_session,ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1),db_session)
    create_annotation_crud(db_session,AnnotationFullCreate(**annotation_data))

    finished_task = finish_task(db_session,1)

    assert finished_task is None, "Step allow_empty_annotation is True, not implemented yet so it should return None"

    step_data_1['allow_empty_annotation'] = False
    update_data_step_crud(1,StepCreate(**step_data_1),db_session)
    
    finished_task = finish_task(db_session,1)
    task = get_task_by_id(db_session,1)

    assert finished_task is None
    assert task.status == TaskStatus.DRAFT, "Task should not be finished because annotation is not DONE"

    finish_annotation_crud(db_session, {"test":"value"},1)

    finished_task = finish_task(db_session,1)
    task = get_task_by_id(db_session,1)

    
    assert finished_task.status is not None
    assert task.status == TaskStatus.DONE, "Task should be finished because annotation is now DONE"

def test_undone_task(db_session: Session):
    
    task = get_task_by_id(db_session,1)

    assert task.status != TaskStatus.PENDING, "Task is not waiting for annotation"

    undone_task(db_session,1)
    task = get_task_by_id(db_session,1)
    
    assert task.status != TaskStatus.PENDING, "Should not change anything because task's annotaton are still DONE"

    skip_annotation_crud(db_session,1)
    undone_task(db_session,1)
    task = get_task_by_id(db_session,1)
    
    assert task.status == TaskStatus.PENDING, "Should have change task's status becaue task's annotation has been skip"



def test_update_data_task_crud(db_session: Session):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    updated_data = {"key": "value updated"}

    update_data_task_crud(
        created_task.id, updated_data, db_session)

    retrieved_updated_task = get_task_by_id(db_session, created_task.id)

    assert retrieved_updated_task is not None
    assert retrieved_updated_task.data == updated_data


def test_delete_task_crud(db_session: Session):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    deleted_task = delete_task_crud(db_session, created_task)

    assert created_task is not None
    assert created_task == deleted_task
    with pytest.raises(GroundControlException):
        retrieved_task = get_task_by_id(db_session, created_task.id)

def test_update_task_status_crud(db_session: Session):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    task = get_task_by_id(db_session,created_task.id)

    assert task.status != TaskStatus.DONE, "Task should be DONE yet"

    update_task_status_crud(db_session,created_task.id,TaskStatus.IN_PROGRESS)

    task = get_task_by_id(db_session,created_task.id)

    assert task.status == TaskStatus.IN_PROGRESS, "Task should be IN_PROGRESS now"

    update_task_status_crud(db_session,created_task.id,TaskStatus.DONE)

    task = get_task_by_id(db_session,created_task.id)

    assert task.status == TaskStatus.DONE, "Task should be DONE now"







