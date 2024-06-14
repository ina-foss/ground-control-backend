import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.services.annotation_service import get_annotations_by_task_id_crud, create_annotation_crud
from src.schemas.annotation_schemas import AnnotationCreate


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


annotation_data = {
    "user_email": "user.email@ina.fr",
    "task_id": 1,
    "project_id": 1,
    "result": {
        "key": "value"
    },
    "status": "DRAFT"
}

annotation_data_2 = {
    "user_email": "user2.email@ina.fr",
    "task_id": 1,
    "project_id": 1,
    "result": {
        "key": "value"
    },
    "status": "DRAFT"
}


def test_create_annotation_crud(db_session: Session):
    """
        Testing annotation creation service
    """
    created_annotation = create_annotation_crud(
        db_session, AnnotationCreate(**annotation_data))

    assert created_annotation is not None
    assert created_annotation.id is not None
    assert created_annotation.user_email == annotation_data["user_email"]
    assert created_annotation.task_id == annotation_data["task_id"]
    assert created_annotation.project_id == annotation_data["project_id"]
    assert created_annotation.result == annotation_data["result"]
    assert created_annotation.status == annotation_data["status"]


def test_get_annotations_by_task_id_crud(db_session: Session):
    """
        Testing getting all the annotation from one task object

        note:
        the assert part looks for retrieved_annotations[1] and retrieved_annotations[2]
        because retrieved_annotations[0] is the one used in the previous test.
    """
    created_annotation_1 = create_annotation_crud(
        db_session, AnnotationCreate(**annotation_data))

    created_annotation_2 = create_annotation_crud(
        db_session, AnnotationCreate(**annotation_data_2))

    retrieved_annotations = get_annotations_by_task_id_crud(db_session, 1)

    assert retrieved_annotations is not None
    assert retrieved_annotations[1].id == created_annotation_1.id
    assert retrieved_annotations[1].user_email == annotation_data["user_email"]
    assert retrieved_annotations[1].task_id == annotation_data["task_id"]
    assert retrieved_annotations[1].project_id == annotation_data["project_id"]
    assert retrieved_annotations[1].result == annotation_data["result"]
    assert retrieved_annotations[1].status == annotation_data["status"]
    assert retrieved_annotations[2].id == created_annotation_2.id
    assert retrieved_annotations[2].user_email == annotation_data_2["user_email"]
    assert retrieved_annotations[2].task_id == annotation_data_2["task_id"]
    assert retrieved_annotations[2].project_id == annotation_data_2["project_id"]
    assert retrieved_annotations[2].result == annotation_data_2["result"]
    assert retrieved_annotations[2].status == annotation_data_2["status"]
