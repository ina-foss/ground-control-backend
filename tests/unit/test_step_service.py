"""Unit tests for Step services"""

# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models import Base
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.services.step_service import (
    create_step_crud,
    delete_step_crud,
    get_step_by_id,
    get_steps,
    update_data_step_crud,
)


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Mock the databalse using sqlite
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def db_session(test_db_engine):
    """
    Create the connection session to interract with sqlite
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_get_steps(db_session: Session):
    step_data_1 = {
        "title": "step 1",
        "description": "la premiere step",
        "annotation_type": "segmentation",
        "status": "draft",
        "pinned_at": "2022-12-27 08:26:49.219717",
        "project_id": 1,
    }

    step_data_2 = {
        "title": "step 2",
        "description": "la deuxieme step",
        "annotation_type": "segmentation",
        "status": "draft",
        "pinned_at": "2022-12-27 08:26:49.219717",
        "project_id": 1,
    }
    created_step_1 = create_step_crud(StepCreate(**step_data_1), db_session)
    created_step_2 = create_step_crud(StepCreate(**step_data_2), db_session)

    retrieved_steps = get_steps(db_session)

    assert retrieved_steps is not None
    assert retrieved_steps[0].id == created_step_1.id
    assert retrieved_steps[0].title == step_data_1["title"]
    assert retrieved_steps[0].description == step_data_1["description"]
    assert retrieved_steps[0].annotation_type.value == step_data_1["annotation_type"]
    assert retrieved_steps[0].status.value == step_data_1["status"]
    assert retrieved_steps[1].project_id == step_data_1["project_id"]
    assert retrieved_steps[1].id == created_step_2.id
    assert retrieved_steps[1].title == step_data_2["title"]
    assert retrieved_steps[1].description == step_data_2["description"]
    assert retrieved_steps[1].annotation_type.value == step_data_2["annotation_type"]
    assert retrieved_steps[1].status.value == step_data_2["status"]
    assert retrieved_steps[1].project_id == step_data_2["project_id"]


step_data = {
    "title": "step 1",
    "description": "la premiere step",
    "annotation_type": "segmentation",
    "status": "draft",
    "pinned_at": "2022-12-27 08:26:49.219717",
    "project_id": 1,
}


def test_create_step_crud(db_session: Session):
    """
    Testing step creation service
    """
    created_step = create_step_crud(StepCreate(**step_data), db_session)
    assert created_step is not None
    assert created_step.id is not None
    assert created_step.title == step_data["title"]
    assert created_step.description == step_data["description"]
    assert created_step.annotation_type.value == step_data["annotation_type"]
    assert created_step.status.value == step_data["status"]
    assert created_step.project_id == step_data["project_id"]


def test_get_step_by_id(db_session: Session):
    created_step = create_step_crud(StepCreate(**step_data), db_session)
    retrieved_step = get_step_by_id(db_session, created_step.id)
    assert retrieved_step is not None
    assert retrieved_step.id == created_step.id
    assert retrieved_step.title == step_data["title"]
    assert retrieved_step.description == step_data["description"]
    assert retrieved_step.annotation_type.value == step_data["annotation_type"]
    assert retrieved_step.status.value == step_data["status"]
    assert retrieved_step.project_id == step_data["project_id"]


def test_get_step_by_inexistant_id(db_session: Session):
    with pytest.raises(GroundControlException):
        get_step_by_id(db_session, 999)


def test_update_step_crud(db_session: Session):
    """
    Test update a step attributes (title, description and author)
    """
    created_step = create_step_crud(StepCreate(**step_data), db_session)

    updated_step_data = {
        "title": "step 3",
        "description": "la troisieme step",
        "annotation_type": "segmentation",
        "status": "draft",
        "pinned_at": "2022-12-27 08:26:49.219717",
        "project_id": 2,
    }
    update_data_step_crud(created_step.id, StepCreate(**updated_step_data), db_session)
    retrieved_updated_step = get_step_by_id(db_session, created_step.id)

    assert retrieved_updated_step is not None
    assert retrieved_updated_step.id == created_step.id
    assert retrieved_updated_step.title == updated_step_data["title"]
    assert retrieved_updated_step.description == updated_step_data["description"]
    assert (
        retrieved_updated_step.annotation_type.value
        == updated_step_data["annotation_type"]
    )
    assert retrieved_updated_step.status.value == updated_step_data["status"]
    assert retrieved_updated_step.project_id == updated_step_data["project_id"]


def test_delete_step_crud(db_session: Session):
    created_step = create_step_crud(StepCreate(**step_data), db_session)

    step = get_step_by_id(db_session, created_step.id)

    assert step is not None

    deleted_step = delete_step_crud(db_session, created_step.id)

    assert deleted_step.id == created_step.id

    with pytest.raises(GroundControlException):
        step = get_step_by_id(db_session, created_step.id)
