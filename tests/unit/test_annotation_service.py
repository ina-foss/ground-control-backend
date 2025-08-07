"""Unit tests for Annotation services"""

# pylint: disable=redefined-outer-name
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models.annotation_model import AnnotationStatus
from ina_ground_control.models.annotation_task_association import (
    AnnotationTask,
    InOutEnum,
)
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.schemas.task_schemas import TaskCreateDto
from ina_ground_control.services.annotation_service import (
    create_annotation_crud,
    finish_annotation_crud,
    get_all_annotations_crud,
    get_annotations_by_id_crud,
    get_annotations_by_task_id_crud,
    skip_annotation_crud,
    udpate_annotation_result_crud,
)
from ina_ground_control.services.project_service import (
    create_project_crud,
    update_project_crud,
)
from ina_ground_control.services.step_service import create_step_crud
from ina_ground_control.services.task_service import create_task_crud

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
    "created_at": "2025-04-27T21:05:01.328292",
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

annotation_data = {
    "annotation": {
        "user_email": "user.email@ina.fr",
        "annotation_status": AnnotationStatus.DRAFT,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
        "created_at": "2025-04-17T08:22:02.235880",
        "updated_at": "2025-04-17T08:25:17.568025",
        "validated_at": "2025-04-17T08:25:17.568025",
    },
    "association": {
        "annotation_id": 1,  # Ensure unique annotation IDs
        "task_id": 1,
        "direction": InOutEnum.IN,
    },
}

annotation_data_2 = {
    "annotation": {
        "user_email": "user2.email@ina.fr",
        "annotation_status": AnnotationStatus.DRAFT,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
        "created_at": "2025-04-17T09:22:02.235880",
        "updated_at": "2025-04-17T09:25:17.568025",
        "validated_at": "2025-04-17T09:25:17.568025",
    },
    "association": {
        "annotation_id": 2,  # Ensure unique annotation IDs
        "task_id": 2,
        "direction": InOutEnum.OUT,
    },
}

annotation_data_3 = {
    "annotation": {
        "user_email": "user.email@ina.fr",
        "annotation_status": AnnotationStatus.IN_PROGRESS,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
        "created_at": "2025-04-10T08:22:02.235880",
        "updated_at": "2025-04-17T08:25:17.568025",
        "validated_at": "2025-04-17T08:25:17.568025",
    },
    "association": {
        "annotation_id": 3,  # Ensure unique annotation IDs
        "task_id": 1,
        "direction": InOutEnum.IN,
    },
}


def test_create_annotation_crud(db_session: Session):
    """
    Testing annotation creation service
    """
    created_annotation = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_3)
    )
    assert created_annotation is not None
    assert created_annotation.id is not None
    assert (
        created_annotation.user_email == annotation_data_3["annotation"]["user_email"]
    )
    assert created_annotation.result == annotation_data_3["annotation"]["result"]
    assert (
        created_annotation.annotation_status
        == annotation_data_3["annotation"]["annotation_status"]
    )
    assert created_annotation.version == annotation_data_3["annotation"]["version"]

    association = (
        db_session.query(AnnotationTask)
        .filter(AnnotationTask.annotation_id == created_annotation.id)
        .first()
    )
    assert association is not None
    assert association.task_id == annotation_data_3["association"]["task_id"]


def test_get_annotation_by_id_crud(db_session: Session):
    created_annotation = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_3)
    )
    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert retrieved_annotation is not None
    assert retrieved_annotation.id == created_annotation.id
    assert retrieved_annotation.user_email == created_annotation.user_email
    assert (
        retrieved_annotation.annotation_status == created_annotation.annotation_status
    )
    assert retrieved_annotation.updated_at == created_annotation.updated_at
    assert retrieved_annotation.created_at == created_annotation.created_at
    assert retrieved_annotation.result == created_annotation.result
    assert retrieved_annotation.version == created_annotation.version

    with pytest.raises(GroundControlException):
        get_annotations_by_id_crud(db_session, 25)


def test_get_annotations_by_task_id_crud(db_session: Session):
    """
    Testing getting all the annotation from one task object
    """
    created_annotation_1 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data)
    )
    created_annotation_2 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_2)
    )
    created_annotation_3 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_3)
    )

    db_session.commit()
    db_session.flush()

    all_satus_annotations_in = get_annotations_by_task_id_crud(
        db_session,
        1,
        "user.email@ina.fr",
        InOutEnum.IN,
        [AnnotationStatus.IN_PROGRESS, AnnotationStatus.DRAFT],
    )
    retrieved_annotations_out = get_annotations_by_task_id_crud(
        db_session, 2, "user2.email@ina.fr", InOutEnum.OUT
    )
    draft_annotation_in = get_annotations_by_task_id_crud(
        db_session, 1, "user.email@ina.fr", InOutEnum.IN, AnnotationStatus.DRAFT
    )

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


def test_update_annotation_result_crud(db_session: Session):
    test_result = {"newResult": "should be this"}
    retrieved_annotation = get_annotations_by_id_crud(db_session, 1)

    assert retrieved_annotation is not None
    assert retrieved_annotation.result == annotation_data_3["annotation"]["result"]

    udpate_annotation_result_crud(db_session, test_result, 1)

    updated_result_annotation = get_annotations_by_id_crud(db_session, 1)

    assert updated_result_annotation is not None
    assert updated_result_annotation.id == retrieved_annotation.id
    assert updated_result_annotation.result == test_result


def test_skip_annotation_crud(db_session: Session):

    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1), db_session)
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
            "direction": InOutEnum.OUT,
        },
    }
    created_annotation = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data)
    )

    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert retrieved_annotation is not None
    assert retrieved_annotation.annotation_status != AnnotationStatus.SKIPPED

    skip_annotation_crud(db_session, created_annotation.id)

    skipped_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert skipped_annotation.annotation_status == AnnotationStatus.SKIPPED
    project_data["allow_skip"] = False

    update_project_crud(db_session, ProjectBaseDto(**project_data), created_project.id)

    with pytest.raises(GroundControlException):
        skip_annotation_crud(db_session, created_annotation.id)


def test_finish_annotation_crud(db_session: Session):
    created_annotation = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data)
    )

    retrieved_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)
    assert retrieved_annotation is not None
    assert retrieved_annotation.annotation_status != AnnotationStatus.DONE

    finish_annotation_crud(
        db_session, retrieved_annotation.result, retrieved_annotation.id
    )

    finished_annotation = get_annotations_by_id_crud(db_session, created_annotation.id)

    assert finished_annotation.annotation_status == AnnotationStatus.DONE


def test_get_all_annotations_crud_filters(db_session: Session):
    """
    Test get_all_annotations_crud filtered according to the provided parameters.
    """
    created_annotation_2 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_2)
    )
    created_annotation_3 = create_annotation_crud(
        db_session, AnnotationFullCreate(**annotation_data_3)
    )

    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))
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
            "annotation_id": 2,  # Ensure unique annotation IDs
            "task_id": created_task.id,
            "direction": InOutEnum.OUT,
        },
    }
    create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data))

    db_session.commit()
    db_session.flush()

    # Filtred by email
    filtered_by_email = get_all_annotations_crud(
        db_session, user_email="user2.email@ina.fr", skip=0, limit=10
    )
    assert len(filtered_by_email) == 2
    assert filtered_by_email[0].user_email == created_annotation_2.user_email

    # Filtred by status
    filtered_by_status = get_all_annotations_crud(
        db_session, status=AnnotationStatus.IN_PROGRESS, skip=0, limit=10
    )
    assert len(filtered_by_status) >= 1
    assert any(a.id == created_annotation_3.id for a in filtered_by_status)

    # Filtrage par project_id
    filtered_by_project = get_all_annotations_crud(
        db_session, project_id=created_project.id, skip=0, limit=10
    )
    assert all(
        a.task.step.project_id == created_project.id for a in filtered_by_project
    )

    # Filtrage par step_id
    filtered_by_step = get_all_annotations_crud(
        db_session, step_id=created_step_1.id, skip=0, limit=10
    )
    assert all(a.task.step_id == created_step_1.id for a in filtered_by_step)

    # Filtred by created_at between
    filtered_by_created_at = get_all_annotations_crud(
        db_session,
        start_created_at=datetime(2025, 4, 17, 8, 0, 0),
        end_created_at=datetime(2025, 4, 17, 10, 0, 0),
        skip=0,
        limit=10,
    )
    assert all(
        datetime(2025, 4, 17, 8, 0, 0)
        <= a.created_at
        <= datetime(2025, 4, 17, 10, 0, 0)
        for a in filtered_by_created_at
    )

    # Filtred by created_at newer
    filtered_by_created_at = get_all_annotations_crud(
        db_session, start_created_at=datetime(2025, 4, 17, 9, 0, 0), skip=0, limit=10
    )
    assert all(
        a.created_at >= datetime(2025, 4, 10, 9, 0, 0) for a in filtered_by_created_at
    )

    # Filtred by created_at older
    filtered_by_created_at = get_all_annotations_crud(
        db_session, end_created_at=datetime(2025, 4, 17, 9, 0, 0), skip=0, limit=10
    )
    assert all(
        a.created_at <= datetime(2025, 4, 10, 9, 0, 0) for a in filtered_by_created_at
    )

    # Filtred by updated_at between
    filtered_by_updated_at = get_all_annotations_crud(
        db_session,
        start_updated_at=datetime(2025, 4, 17, 8, 0, 0),
        end_updated_at=datetime(2025, 4, 17, 10, 0, 0),
        skip=0,
        limit=10,
    )
    assert all(
        datetime(2025, 4, 17, 8, 0, 0)
        <= a.updated_at
        <= datetime(2025, 4, 17, 10, 0, 0)
        for a in filtered_by_updated_at
    )

    # Filtred by updated_at newer
    filtered_by_updated_at = get_all_annotations_crud(
        db_session, start_updated_at=datetime(2025, 4, 17, 9, 0, 0), skip=0, limit=10
    )
    assert all(
        a.updated_at >= datetime(2025, 4, 17, 9, 0, 0) for a in filtered_by_updated_at
    )

    # Filtred by updated_at older
    filtered_by_updated_at = get_all_annotations_crud(
        db_session, end_updated_at=datetime(2025, 4, 17, 9, 0, 0), skip=0, limit=10
    )
    assert all(
        a.updated_at <= datetime(2025, 4, 17, 9, 0, 0) for a in filtered_by_updated_at
    )

    # Filtred by validated_at between
    filtered_by_validated_at = get_all_annotations_crud(
        db_session,
        start_validated_at=datetime(2025, 4, 17, 8, 0, 0),
        end_validated_at=datetime(2025, 4, 17, 10, 0, 0),
        skip=0,
        limit=10,
    )
    assert all(
        datetime(2025, 4, 17, 8, 0, 0)
        <= a.validated_at
        <= datetime(2025, 4, 17, 10, 0, 0)
        for a in filtered_by_validated_at
    )

    # Filtred by validated_at older
    filtered_by_validated_at = get_all_annotations_crud(
        db_session, end_validated_at=datetime(2025, 4, 17, 9, 0, 0), skip=0, limit=10
    )
    assert all(
        a.validated_at <= datetime(2025, 4, 10, 9, 0, 0)
        for a in filtered_by_validated_at
    )

    # Filtred by validated_at newer
    filtered_by_validated_at = get_all_annotations_crud(
        db_session, start_validated_at=datetime(2025, 4, 17, 9, 30, 0), skip=0, limit=10
    )
    assert all(
        a.validated_at >= datetime(2025, 4, 17, 9, 30, 0)
        for a in filtered_by_validated_at
    )

    # Pagination
    paginated_annotations = get_all_annotations_crud(db_session, skip=0, limit=2)
    assert len(paginated_annotations) <= 2
