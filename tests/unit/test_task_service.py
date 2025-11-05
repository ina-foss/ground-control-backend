"""Unit tests for Task services"""

# pylint: disable=redefined-outer-name
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models import Base
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import (
    AnnotationTask,
    InOutEnum,
)
from ina_ground_control.models.step_model import StepStatus
from ina_ground_control.models.task_model import Task
from ina_ground_control.schemas.annotation_schemas import (
    AnnotationFullCreate,
    AnnotationStatus,
)
from ina_ground_control.schemas.project_schemas import ProjectBaseDto, ProjectStatus
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.schemas.task_schemas import TaskCreateDto, TaskStatus
from ina_ground_control.services.annotation_service import (
    create_annotation_crud,
    finish_annotation_crud,
)
from ina_ground_control.services.project_service import (
    create_project_crud,
    get_project_by_id,
)
from ina_ground_control.services.step_service import (
    create_step_crud,
    get_step_by_id,
    update_step_status_crud,
)
from ina_ground_control.services.task_service import (
    create_task_crud,
    delete_task_crud,
    get_task_by_id,
    recalculate_project_status,
    recalculate_step_status,
    recalculate_task_status,
    update_data_task_crud,
    update_task_status_crud,
)


@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def db_session(test_db_engine):
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
    "id": 1,
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
    "created_at": "2025-04-27T21:05:01.328292",
}

step_data_1 = {
    "title": "step 1",
    "description": "la premiere step",
    "annotation_type": "segmentation",
    "status": StepStatus.DRAFT,
    "pinned_at": "2022-12-27 08:26:49.219717",
    "project_id": 1,
    "allow_empty_annotation": True,
    "id": 1,
    "redundancy": 1,
    "max_tasks_per_person": 1,
    "completeness_rate": 100.0,
}


def test_get_task_by_id(db_session: SQLAlchemySession):
    create_project_crud(db_session, ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1), db_session)
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)
    retrieved_task = get_task_by_id(db_session, created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == task_data["name"]
    assert retrieved_task.instruction == task_data["instruction"]
    assert retrieved_task.data_type.value == task_data["data_type"]
    assert retrieved_task.status == task_data["status"]
    assert retrieved_task.lead_time == task_data["lead_time"]
    assert retrieved_task.step_id == task_data["step_id"]
    assert retrieved_task.media_id == task_data["media_id"]


def test_create_task_crud(db_session: SQLAlchemySession):
    create_project_crud(db_session, ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1), db_session)
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)
    assert created_task is not None
    assert created_task.id is not None
    assert created_task.name == task_data["name"]
    assert created_task.instruction == task_data["instruction"]
    assert created_task.data_type.value == task_data["data_type"]
    assert created_task.status == task_data["status"]
    assert created_task.lead_time == task_data["lead_time"]
    assert created_task.step_id == task_data["step_id"]
    assert created_task.media_id == task_data["media_id"]


def test_update_data_task_crud(db_session: SQLAlchemySession):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)
    update_payload = {
        "name": "Updated Task",
        "instruction": "Updated instruction",
        "lead_time": 5,
    }
    updated_task = update_data_task_crud(created_task.id, update_payload, db_session)
    assert updated_task is not None
    assert updated_task.id == created_task.id
    assert updated_task.name == "Updated Task"
    assert updated_task.instruction == "Updated instruction"
    assert updated_task.lead_time == 5


def test_delete_task_crud(db_session: SQLAlchemySession):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    deleted_task = delete_task_crud(db_session, created_task)
    assert created_task is not None
    assert created_task == deleted_task
    with pytest.raises(GroundControlException):
        get_task_by_id(db_session, created_task.id)


def test_update_task_status_crud(db_session: SQLAlchemySession):
    created_task = create_task_crud(TaskCreateDto(**task_data), db_session)

    task = get_task_by_id(db_session, created_task.id)
    assert task.status != TaskStatus.DONE, "Task should be DONE yet"

    update_task_status_crud(db_session, created_task.id, TaskStatus.IN_PROGRESS)

    task = get_task_by_id(db_session, created_task.id)
    assert task.status == TaskStatus.IN_PROGRESS, "Task should be IN_PROGRESS now"

    update_task_status_crud(db_session, created_task.id, TaskStatus.DONE)

    task = get_task_by_id(db_session, created_task.id)
    assert task.status == TaskStatus.DONE, "Task should be DONE now"


def create_task_with_annotations(db: SQLAlchemySession, expired: bool = True):
    expiration_date = (
        datetime.now(timezone.utc) - timedelta(days=1)
        if expired
        else datetime.now(timezone.utc) + timedelta(days=1)
    )
    task = Task(name="test", expiration_date=expiration_date, status=TaskStatus.PENDING)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Ajout des annotations IN et OUT
    for direction in [InOutEnum.IN, InOutEnum.OUT]:
        annotation = Annotation(
            annotation_status=AnnotationStatus.PENDING, user_email="test@test.fr"
        )
        db.add(annotation)
        db.commit()
        db.refresh(annotation)
        annotation_task = AnnotationTask(
            annotation_id=annotation.id, task_id=task.id, direction=direction
        )
        db.add(annotation_task)

    db.commit()
    return task


def test_recalculate_task_status(db_session: SQLAlchemySession):
    # Case 1: Task is DRAFT → should become PENDING if redundancy > 0
    task = create_task_crud(TaskCreateDto(**task_data), db_session)
    task.status = TaskStatus.DRAFT
    task.redundancy = 1  # ensure redundancy > 0
    db_session.commit()

    recalculate_task_status(db_session, task.id)
    task_refreshed = get_task_by_id(db_session, task.id)
    assert task_refreshed.status == TaskStatus.PENDING

    # Case 2: Task is PENDING → stays PENDING
    task_2 = create_task_crud(
        TaskCreateDto(**{**task_data, "status": TaskStatus.PENDING}), db_session
    )
    recalculate_task_status(db_session, task_2.id)
    task_2_refreshed = get_task_by_id(db_session, task_2.id)
    assert task_2_refreshed.status == TaskStatus.PENDING

    # Case 3: Task is IN_PROGRESS → becomes DONE after enough DONE annotations
    task_3 = create_task_crud(
        TaskCreateDto(
            **{**task_data, "status": TaskStatus.IN_PROGRESS, "redundancy": 1}
        ),
        db_session,
    )

    # Create a DONE annotation
    annotation_data = {
        "annotation": {
            "user_email": "user.email@ina.fr",
            "annotation_status": AnnotationStatus.DONE,
            "version": 1,
            "result": {"toto1": "test"},
        },
        "association": {
            "annotation_id": 1,
            "task_id": task_3.id,
            "direction": InOutEnum.OUT,
        },
    }
    annotation = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data)
    )

    # Recalculate task status
    recalculate_task_status(db_session, task_3.id)
    task_3_refreshed = get_task_by_id(db_session, task_3.id)
    assert task_3_refreshed.status == TaskStatus.DONE


def test_recalculate_step_status(db_session):
    create_project_crud(db_session, ProjectBaseDto(**project_data))
    step = create_step_crud(StepCreate(**step_data_1), db_session)

    # 1. All tasks PENDING -> Step should be PENDING
    create_task_crud(
        TaskCreateDto(
            **{**task_data, "status": TaskStatus.PENDING, "step_id": step.id}
        ),
        db_session,
    )
    create_task_crud(
        TaskCreateDto(
            **{
                **task_data,
                "name": "task2",
                "status": TaskStatus.PENDING,
                "step_id": step.id,
            }
        ),
        db_session,
    )
    recalculate_step_status(db_session, step.id)
    assert get_step_by_id(db_session, step.id).status == StepStatus.PENDING

    # 2. Some tasks DONE, some PENDING -> Step should be IN_PROGRESS
    create_task_crud(
        TaskCreateDto(**{**task_data, "status": TaskStatus.DONE, "step_id": step.id}),
        db_session,
    )
    recalculate_step_status(db_session, step.id)
    assert get_step_by_id(db_session, step.id).status == StepStatus.IN_PROGRESS


def test_recalculate_project_status(db_session):
    # Create project
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    # STEP 1: All steps are PENDING → project should be PENDING
    step1 = create_step_crud(
        StepCreate(
            **{**step_data_1, "project_id": project.id, "status": StepStatus.PENDING}
        ),
        db_session,
    )
    step2 = create_step_crud(
        StepCreate(
            **{
                **step_data_1,
                "name": "Step 2",
                "project_id": project.id,
                "status": StepStatus.PENDING,
            }
        ),
        db_session,
    )

    recalculate_project_status(db_session, project.id)
    assert get_project_by_id(db_session, project.id).status == ProjectStatus.PENDING

    # STEP 2: One step is DONE, one is PENDING → project should be IN_PROGRESS
    update_step_status_crud(db_session, step1, StepStatus.DONE)
    recalculate_project_status(db_session, project.id)
    assert get_project_by_id(db_session, project.id).status == ProjectStatus.IN_PROGRESS

    # STEP 3: All steps are DONE → project should be DONE
    update_step_status_crud(db_session, step2, StepStatus.DONE)
    recalculate_project_status(db_session, project.id)
    assert get_project_by_id(db_session, project.id).status == ProjectStatus.DONE

    # STEP 4: All steps are SKIPPED or DRAFT → project should be PENDING
    update_step_status_crud(db_session, step1, StepStatus.SKIPPED)
    update_step_status_crud(db_session, step2, StepStatus.DRAFT)
    recalculate_project_status(db_session, project.id)
    assert get_project_by_id(db_session, project.id).status == ProjectStatus.IN_PROGRESS
