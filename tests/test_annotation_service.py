import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.models.annotation_task_association import AnnotationTask, InOutEnum
from ina_ground_control.services.annotation_service import get_annotations_by_task_id_crud, create_annotation_crud
from ina_ground_control.schemas.annotation_schemas import AnnotationCreate, AnnotationFullCreate


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
    "annotation": {
        "user_email": "user.email@ina.fr",
        "annotation_status": "draft",
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 1,  # Ensure unique annotation IDs
        "task_id": 1,
        "direction": InOutEnum.IN
    }
}

annotation_data_2 = {
    "annotation": {
        "user_email": "user2.email@ina.fr",
        "annotation_status": "draft",
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 2,  # Ensure unique annotation IDs
        "task_id": 2,
        "direction": InOutEnum.OUT
    }
}

annotation_data_3 = {
    "annotation": {
        "user_email": "user.email@ina.fr",
        "annotation_status": "draft",
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 3,  # Ensure unique annotation IDs
        "task_id": 3,
        "direction": InOutEnum.OUT
    }
}


def test_create_annotation_crud(db_session: Session):
    """
    Testing annotation creation service
    """
    created_annotation = create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data_3))

    assert created_annotation is not None
    assert created_annotation.id is not None
    assert created_annotation.user_email == annotation_data_3["annotation"]["user_email"]
    assert created_annotation.result == annotation_data_3["annotation"]["result"]
    assert created_annotation.annotation_status.value == annotation_data_3["annotation"]["annotation_status"]
    assert created_annotation.version == annotation_data_3["annotation"]["version"]

    association = db_session.query(AnnotationTask).filter(AnnotationTask.annotation_id == created_annotation.id).first()
    assert association is not None
    assert association.task_id == annotation_data_3["association"]["task_id"]


def test_get_annotations_by_task_id_crud(db_session: Session):
    """
    Testing getting all the annotation from one task object
    """
    created_annotation_1 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data))
    created_annotation_2 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_2))

    db_session.commit()
    db_session.flush()

    retrieved_annotations_in = get_annotations_by_task_id_crud(db_session, 1, InOutEnum.IN,"")
    retrieved_annotations_out = get_annotations_by_task_id_crud(db_session, 2, InOutEnum.OUT,"")

    assert retrieved_annotations_in is not None
    assert len(retrieved_annotations_in) == 1
    assert retrieved_annotations_in[0].id == created_annotation_1.id

    assert retrieved_annotations_out is not None
    assert len(retrieved_annotations_out) == 1
    assert retrieved_annotations_out[0].id == created_annotation_2.id
