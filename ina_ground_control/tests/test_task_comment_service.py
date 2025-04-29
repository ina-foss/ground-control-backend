"""Unit tests for Task Comment services"""
# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from ina_ground_control.database import Base
from ina_ground_control.schemas.task_comment_schemas import TaskCommentCreate
from ina_ground_control.services.task_comment_service import get_task_comment_by_id, create_task_comment_crud, \
    update_task_comment_crud, delete_task_comment_crud, get_task_comments, get_task_comment_by_task_id


@pytest.fixture(scope="session")
def db_engine():
    """
        Mock the databalse using sqlite
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def db_session(db_engine):
    """
        Create the connection session to interract with sqlite
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_get_task_comments(db_session: Session):
    task_comment_data_1 = {
        "comment": "test A",
        "task_id": 1,
        "created_by": "admin@localhost.com"
    }
    task_comment_data_2 = {
        "comment": "test B",
        "task_id": 2,
        "created_by": "admin@localhost.com"
    }
    created_task_comment_1 = create_task_comment_crud(TaskCommentCreate(**task_comment_data_1), db_session)
    created_task_comment_2 = create_task_comment_crud(TaskCommentCreate(**task_comment_data_2), db_session)

    retrieved_task_comments = get_task_comments(db_session)

    assert retrieved_task_comments is not None
    assert retrieved_task_comments[0].id == created_task_comment_1.id
    assert retrieved_task_comments[0].comment == task_comment_data_1["comment"]
    assert retrieved_task_comments[0].task_id == task_comment_data_1["task_id"]
    assert retrieved_task_comments[1].id == created_task_comment_2.id
    assert retrieved_task_comments[1].comment == task_comment_data_2["comment"]
    assert retrieved_task_comments[1].task_id == task_comment_data_2["task_id"]


task_comment_data = {
    "comment": "test A",
    "task_id": 1,
    "created_by": "admin@localhost.com"
}


def test_get_task_comment_by_id(db_session: Session):
    created_task_comment = create_task_comment_crud(TaskCommentCreate(**task_comment_data), db_session)

    retrieved_task_comment = get_task_comment_by_id(db_session, created_task_comment.id)

    assert retrieved_task_comment is not None
    assert retrieved_task_comment.id == created_task_comment.id
    assert retrieved_task_comment.comment == task_comment_data["comment"]
    assert retrieved_task_comment.task_id == task_comment_data["task_id"]


def test_get_task_comment_by_task_id(db_session: Session):
    task_comment_data_1 = {
        "comment": "test A",
        "task_id": 3,
        "created_by": "admin@localhost.com"
    }
    task_comment_data_2 = {
        "comment": "test B",
        "task_id": 3,
        "created_by": "admin@localhost.com"
    }

    created_task_comment_1 = create_task_comment_crud(TaskCommentCreate(**task_comment_data_1), db_session)
    created_task_comment_2 = create_task_comment_crud(TaskCommentCreate(**task_comment_data_2), db_session)

    retrieved_task_comments = get_task_comment_by_task_id(db_session, created_task_comment_1.task_id)

    assert retrieved_task_comments is not None
    assert len(retrieved_task_comments) == 2
    assert retrieved_task_comments[0].id == created_task_comment_1.id
    assert retrieved_task_comments[0].comment == task_comment_data_1["comment"]
    assert retrieved_task_comments[1].id == created_task_comment_2.id
    assert retrieved_task_comments[1].comment == task_comment_data_2["comment"]


def test_create_task_comment_crud(db_session: Session):
    """
        Testing taskComment creation service
    """
    created_task_comment = create_task_comment_crud(TaskCommentCreate(**task_comment_data), db_session)

    assert created_task_comment is not None
    assert created_task_comment.id is not None
    assert created_task_comment.comment == task_comment_data["comment"]
    assert created_task_comment.task_id == task_comment_data["task_id"]


def test_update_data_task_comment_crud(db_session: Session):
    created_task_comment = create_task_comment_crud(TaskCommentCreate(**task_comment_data), db_session)
    updated_task_comment_data = {
        "comment": "test B",
        "task_id": 6,
        "created_by": "admin@localhost.com"
    }
    update_task_comment_crud(created_task_comment.id, TaskCommentCreate(**updated_task_comment_data), db_session)
    retrieved_updated_task_comment = get_task_comment_by_id(db_session, created_task_comment.id)

    assert retrieved_updated_task_comment is not None
    assert retrieved_updated_task_comment.comment == updated_task_comment_data["comment"]
    assert retrieved_updated_task_comment.task_id == updated_task_comment_data["task_id"]


def test_delete_task_comment_crud(db_session: Session):
    created_task_comment = create_task_comment_crud(TaskCommentCreate(**task_comment_data), db_session)
    delete_task_comment_crud(db_session, created_task_comment.id)
    retrieved_task_comment = get_task_comment_by_id(db_session, created_task_comment.id)

    assert created_task_comment is not None
    assert retrieved_task_comment is None
