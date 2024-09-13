import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.schemas.task_comment_schemas import TaskCommentCreate , TaskCommentDto
from ina_ground_control.services.task_comment_service import get_task_comment_by_id, create_task_comment_crud, update_task_comment_crud,delete_task_comment_crud,get_task_comments



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
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_get_taskComments(db_session: Session):
    taskComment_data_1 = {
        "comment": "test A",
        "task_id": 1
    }
    taskComment_data_2 = {
        "comment": "test B",
        "task_id": 2
    }
    created_taskComment_1 = create_task_comment_crud(TaskCommentCreate(**taskComment_data_1), db_session)
    created_taskComment_2 = create_task_comment_crud(TaskCommentCreate(**taskComment_data_2), db_session)

    retrieved_taskComments = get_task_comments(db_session)

    assert retrieved_taskComments is not None
    assert retrieved_taskComments[0].id == created_taskComment_1.id
    assert retrieved_taskComments[0].comment == taskComment_data_1["comment"]
    assert retrieved_taskComments[0].task_id == taskComment_data_1["task_id"]
    assert retrieved_taskComments[1].id == created_taskComment_2.id
    assert retrieved_taskComments[1].comment == taskComment_data_2["comment"]
    assert retrieved_taskComments[1].task_id == taskComment_data_2["task_id"]

taskComment_data = {
        "comment": "test A",
        "task_id": 1
    }
def test_get_taskComment_by_id(db_session: Session):

    created_taskComment = create_task_comment_crud(TaskCommentCreate(**taskComment_data), db_session)

    retrieved_taskComment = get_task_comment_by_id(db_session, created_taskComment.id)

    assert retrieved_taskComment is not None
    assert retrieved_taskComment.id == created_taskComment.id
    assert retrieved_taskComment.comment == taskComment_data["comment"]
    assert retrieved_taskComment.task_id == taskComment_data["task_id"]

def test_create_taskComment_crud(db_session: Session):
    """
        Testing taskComment creation service
    """
    created_taskComment = create_task_comment_crud(TaskCommentCreate(**taskComment_data), db_session)

    assert created_taskComment is not None
    assert created_taskComment.id is not None
    assert created_taskComment.comment == taskComment_data["comment"]
    assert created_taskComment.task_id == taskComment_data["task_id"]


def test_update_data_taskComment_crud(db_session: Session):
    created_taskComment = create_task_comment_crud(TaskCommentCreate(**taskComment_data), db_session)
    updated_taskComment_data = {
        "comment": "test B",
        "task_id": 6
    }
    update_task_comment_crud(created_taskComment.id, TaskCommentCreate(**updated_taskComment_data), db_session)
    retrieved_updated_taskComment = get_task_comment_by_id(db_session, created_taskComment.id)

    assert retrieved_updated_taskComment is not None
    assert retrieved_updated_taskComment.comment == updated_taskComment_data["comment"]
    assert retrieved_updated_taskComment.task_id == updated_taskComment_data["task_id"]

def test_delete_taskComment_crud(db_session: Session):
    created_taskComment = create_task_comment_crud(TaskCommentCreate(**taskComment_data), db_session)
    delete_task_comment_crud(db_session, created_taskComment.id)
    retrieved_taskComment = get_task_comment_by_id(db_session, created_taskComment.id)

    assert created_taskComment is not None
    assert retrieved_taskComment is None

