import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from ina_ground_control.database import Base
from ina_ground_control.models.annotation_task_association import AnnotationTask, InOutEnum
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.schemas.task_schemas import TaskCreateDto
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.services.annotation_service import finish_annotation_crud, get_annotations_by_task_id_crud, create_annotation_crud, get_annotations_by_id_crud, skip_annotation_crud, udpate_annotation_result_crud
from ina_ground_control.services.step_service import create_step_crud
from ina_ground_control.services.task_service import create_task_crud
from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models.annotation_model import AnnotationStatus
from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.services.project_service import create_project_crud, update_project_crud


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
        "annotation_status": AnnotationStatus.DRAFT,
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
        "annotation_status": AnnotationStatus.DRAFT,
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
        "annotation_status": AnnotationStatus.IN_PROGRESS,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 3,  # Ensure unique annotation IDs
        "task_id": 1,
        "direction": InOutEnum.IN
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
    assert created_annotation.annotation_status == annotation_data_3["annotation"]["annotation_status"]
    assert created_annotation.version == annotation_data_3["annotation"]["version"]

    association = db_session.query(AnnotationTask).filter(AnnotationTask.annotation_id == created_annotation.id).first()
    assert association is not None
    assert association.task_id == annotation_data_3["association"]["task_id"]


def test_get_annotation_by_id_crud(db_session: Session):
    created_annotation = create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data_3))
    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    
    assert retrieved_annotation is not None
    assert retrieved_annotation.id == created_annotation.id
    assert retrieved_annotation.user_email == created_annotation.user_email
    assert retrieved_annotation.annotation_status == created_annotation.annotation_status
    assert retrieved_annotation.updated_at == created_annotation.updated_at
    assert retrieved_annotation.created_at == created_annotation.created_at
    assert retrieved_annotation.result == created_annotation.result
    assert retrieved_annotation.version == created_annotation.version

    with pytest.raises(GroundControlException):
        get_annotations_by_id_crud(db_session,25)

def test_get_annotations_by_task_id_crud(db_session: Session):
    """
    Testing getting all the annotation from one task object
    """
    created_annotation_1 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data))
    created_annotation_2 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_2))
    created_annotation_3 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_3))

    db_session.commit()
    db_session.flush()

    all_satus_annotations_in = get_annotations_by_task_id_crud(db_session, 1, "user.email@ina.fr", InOutEnum.IN,[AnnotationStatus.IN_PROGRESS,AnnotationStatus.DRAFT] )
    retrieved_annotations_out = get_annotations_by_task_id_crud(db_session, 2, "user2.email@ina.fr", InOutEnum.OUT)
    draft_annotation_in = get_annotations_by_task_id_crud(db_session, 1, "user.email@ina.fr", InOutEnum.IN, AnnotationStatus.DRAFT)

    assert all_satus_annotations_in is not None
    assert len(all_satus_annotations_in) == 4
    assert all_satus_annotations_in[2].id == created_annotation_1.id
    assert all_satus_annotations_in[3].id == created_annotation_3.id

    assert retrieved_annotations_out is not None
    assert len(retrieved_annotations_out) == 1
    assert retrieved_annotations_out[0].id == created_annotation_2.id

    assert draft_annotation_in is not None
    assert len(draft_annotation_in) == 1
    assert draft_annotation_in[0].id == created_annotation_1.id

def test_update_annotation_result_crud(db_session:Session):
    test_result = {"newResult":"should be this"}
    retrieved_annotation = get_annotations_by_id_crud(db_session,1)

    assert retrieved_annotation is not None
    assert retrieved_annotation.result == annotation_data_3['annotation']['result']

    udpate_annotation_result_crud(db_session,test_result,1)

    updated_result_annotation = get_annotations_by_id_crud(db_session,1)

    assert updated_result_annotation is not None
    assert updated_result_annotation.id == retrieved_annotation.id
    assert updated_result_annotation.result == test_result


def test_skip_annotation_crud(db_session: Session):
    step_data_1 = {
        "title": "step 1",
        "description": "la premiere step",
        "annotation_type": "segmentation",
        "status": "draft",
        "pinned_at": "2022-12-27 08:26:49.219717",
        "project_id": 1,
    }
    task_data = {
        "name": "Test Task",
        "instruction": "Test instruction",
        "data": {"key": "value"},
        "data_type": "ldd",
        "status": "draft",
        "lead_time": 1,
        "step_id": 1,
        "media_id": 1,
    }
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



    created_project = create_project_crud(db_session,ProjectBaseDto(**project_data))
    created_step_1 = create_step_crud(StepCreate(**step_data_1), db_session)
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    annotation_data = {
        "annotation": {
            "user_email": "user.email@ina.fr",
 "annotation_status": "draft",
            "version": 1,
            "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
        },
        "association": {
            "annotation_id": 1,  # Ensure unique annotation IDs
            "task_id": created_task.id,
            "direction": InOutEnum.OUT
        }
    }
    created_annotation = create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data))

    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert retrieved_annotation is not None
    assert retrieved_annotation.annotation_status != AnnotationStatus.SKIPPED

    skip_annotation_crud(db_session,created_annotation.id)

    skipped_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    
    assert skipped_annotation.annotation_status == AnnotationStatus.SKIPPED

    project_data['allow_skip'] = False

    update_project_crud(db_session,ProjectBaseDto(**project_data),created_project.id)

    with pytest.raises(GroundControlException):
        skip_annotation_crud(db_session,created_annotation.id)


def test_finish_annotation_crud(db_session: Session):
    created_annotation = create_annotation_crud(db_session,AnnotationFullCreate(**annotation_data))

    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert retrieved_annotation is not None
    assert retrieved_annotation.annotation_status != AnnotationStatus.DONE

    finish_annotation_crud(db_session, retrieved_annotation.result,retrieved_annotation.id)

    finished_annotation = get_annotations_by_id_crud(db_session,created_annotation.id)

    assert finished_annotation.annotation_status == AnnotationStatus.DONE


