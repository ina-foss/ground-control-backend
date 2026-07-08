"""Unit tests for Project services"""

import pytest
from sqlalchemy.orm import Session as SQLAlchemySession

from ina_ground_control.constants.enums import Status
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.schemas.project_schemas import ProjectBaseDto, ProjectUpdateDto
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.schemas.task_schemas import TaskCreateDto, TaskWithIdDto
from ina_ground_control.services.annotation_service import create_annotation_crud
from ina_ground_control.services.project_service import (
    _get_relevant_tasks_for_projects,
    archive_project_service,
    create_project_crud,
    delete_project_crud,
    finish_project_service,
    get_progressed_tasks_count_for_project_service,
    get_project_by_id,
    unarchive_project_service,
    update_project_crud,
)
from ina_ground_control.services.step_service import create_step_crud
from ina_ground_control.services.task_service import create_task_crud

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
    "status": Status.DRAFT,
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
    "status": Status.DRAFT,
    "pinned_at": "2022-12-27 08:26:49.219717",
    "project_id": 1,
    "allow_empty_annotation": True,
    "id": 1,
    "redundancy": 1,
    "max_tasks_per_person": 1,
    "completeness_rate": 100.0,
}

annotation_data = {
    "annotation": {
        "user_email": "user.email@ina.fr",
        "annotation_status": Status.IN_PROGRESS,
        "version": 1,
        "result": {"toto1": "test", "toto2": "test", "toto3": "test"},
    },
    "association": {
        "annotation_id": 1,
        "task_id": 1,
        "direction": InOutEnum.OUT,
    },
}


def test_get_project_by_id(db_session: SQLAlchemySession):
    """
    Test to get a singualr project given its id.
    """
    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    retrieved_project = get_project_by_id(db_session, created_project.id)

    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.title == project_data["title"]
    assert retrieved_project.description == project_data["description"]
    assert retrieved_project.created_by == project_data["created_by"]


def test_create_project_crud(db_session: SQLAlchemySession):
    """
    Test the creation of a project
    """
    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    assert created_project is not None
    assert created_project.id is not None
    assert created_project.title == project_data["title"]
    assert created_project.description == project_data["description"]
    assert created_project.created_by == project_data["created_by"]


def test_update_project_crud(db_session: SQLAlchemySession):
    created_project = create_project_crud(
        db_session,
        ProjectBaseDto(**project_data),
    )

    updated_task_data = {
        "title": "Test Project 2",
        "description": "Test description 2",
    }

    update_project_crud(
        db_session,
        ProjectUpdateDto(**updated_task_data),
        created_project.id,
        "jane@example.com",
    )

    retrieved_updated_project = get_project_by_id(db_session, created_project.id)

    assert retrieved_updated_project is not None
    assert retrieved_updated_project.title == updated_task_data["title"]
    assert retrieved_updated_project.description == updated_task_data["description"]
    assert retrieved_updated_project.updated_by == "jane@example.com"


def test_delete_project_crud(db_session: SQLAlchemySession):
    """
    Test the deletion of a project given its id
    """
    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    delete_project_crud(db_session, created_project.id)

    retrieved_project = get_project_by_id(db_session, created_project.id)

    assert created_project is not None
    assert retrieved_project is None


def test_finish_project_service(db_session: SQLAlchemySession):
    """
    Test that finish_project_service sets project, steps, and tasks to DONE
    """
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    step = project.steps[0] if project.steps else None
    if step:
        for task in step.tasks:
            task.status = Status.DRAFT
    db_session.commit()
    finish_project_service(db_session, project.id)
    retrieved_project = get_project_by_id(db_session, project.id)
    assert retrieved_project.status == Status.DONE
    for step in retrieved_project.steps:
        assert step.status == Status.DONE
        for task in step.tasks:
            assert task.status == Status.DONE


def test_get_progressed_tasks_for_project_service(db_session: SQLAlchemySession):
    """
    Test that get_progressed_tasks_for_project_service returns only tasks
    with IN_PROGRESS status for a given project.
    """
    task_status = Status.DONE
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    for step in project.steps:
        for task in step.tasks:
            task.status = task_status
    db_session.commit()

    count = get_progressed_tasks_count_for_project_service(db_session, project.id)
    assert isinstance(count, int)
    assert count == 0


def test_get_progressed_tasks_for_nonexistent_project(db_session: SQLAlchemySession):
    """
    Test that requesting in-progress tasks for a nonexistent project
    raises GroundControlException with RESOURCE_NOT_FOUND.
    """
    non_existing_project_id = 9999
    with pytest.raises(GroundControlException) as exc_info:
        get_progressed_tasks_count_for_project_service(
            db_session, non_existing_project_id
        )
    assert exc_info.value.code == ErrorCode.RESOURCE_NOT_FOUND.value[0]


def test_archive_project_service_success(db_session: SQLAlchemySession):
    """
    Test successful archival of a project and its related entities.
    """
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1), db_session)
    create_task_crud(TaskCreateDto(**task_data), db_session)
    create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data))
    archived_project = archive_project_service(db_session, project.id)

    assert archived_project.status == Status.ARCHIVED
    assert archived_project.previous_status == Status.DRAFT

    for step in archived_project.steps:
        assert step.status == Status.ARCHIVED
        assert step.previous_status == Status.DRAFT
        for task in step.tasks:
            assert task.status == Status.ARCHIVED
            assert task.previous_status == Status.DRAFT
            for annotation in task.annotations:
                assert annotation.status == Status.ARCHIVED
                assert annotation.previous_status == Status.DRAFT

    refreshed = get_project_by_id(db_session, project.id)
    assert refreshed.status == Status.ARCHIVED


def test_archive_project_service_not_found(db_session: SQLAlchemySession):
    """
    Test that an exception is raised if the project does not exist.
    """
    with pytest.raises(GroundControlException) as exc:
        archive_project_service(db_session, project_id=9999)

    assert exc.value.code == ErrorCode.RESOURCE_NOT_FOUND.name


def test_archive_project_service_already_archived(db_session: SQLAlchemySession):
    """
    Test that trying to archive an already archived project raises an error.
    """
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    project.status = Status.ARCHIVED
    db_session.commit()

    with pytest.raises(GroundControlException) as exc:
        archive_project_service(db_session, project.id)

    assert exc.value.code == ErrorCode.BAD_REQUEST.name


def test_archive_project_service_done_project(db_session: SQLAlchemySession):
    """
    Test that trying to archive a completed (DONE) project raises an error.
    """
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    project.status = Status.DONE
    db_session.commit()

    with pytest.raises(GroundControlException) as exc:
        archive_project_service(db_session, project.id)

    assert exc.value.code == ErrorCode.BAD_REQUEST.name


def test_unarchive_project_service_success(db_session: SQLAlchemySession):
    """
    Test successful unarchival of a previously archived project and its related entities.
    """
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    create_step_crud(StepCreate(**step_data_1), db_session)
    create_task_crud(TaskCreateDto(**task_data), db_session)
    create_annotation_crud(db_session, AnnotationFullCreate(**annotation_data))

    archived_project = archive_project_service(db_session, project.id)

    assert archived_project.status == Status.ARCHIVED
    assert archived_project.previous_status == Status.DRAFT

    unarchived_project = unarchive_project_service(db_session, project.id)

    assert unarchived_project.status == Status.DRAFT
    assert unarchived_project.previous_status is None

    for step in unarchived_project.steps:
        assert step.status == Status.DRAFT
        assert step.previous_status is None
        for task in step.tasks:
            assert task.status == Status.DRAFT
            assert task.previous_status is None
            for annotation in task.annotations:
                assert annotation.annotation_status == Status.DRAFT
                assert annotation.previous_status is None

    refreshed = get_project_by_id(db_session, project.id)
    assert refreshed.status == Status.DRAFT
    assert refreshed.previous_status is None


def test_unarchive_project_not_found(db_session: SQLAlchemySession):
    with pytest.raises(GroundControlException) as exc:
        unarchive_project_service(db_session, project_id=9999)
    assert exc.value.code == ErrorCode.RESOURCE_NOT_FOUND.name


def test_unarchive_done_project(db_session: SQLAlchemySession):
    project_data["status"] = Status.DONE
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))
    with pytest.raises(GroundControlException) as exc:
        unarchive_project_service(db_session, project.id)
    assert exc.value.code == ErrorCode.BAD_REQUEST.name


def test_get_relevant_tasks_excludes_done_tasks_for_current_user(
    db_session: SQLAlchemySession,
):
    project = create_project_crud(
        db_session,
        ProjectBaseDto(**project_data),
    )

    step = create_step_crud(
        StepCreate(
            **{
                **step_data_1,
                "project_id": project.id,
            }
        ),
        db_session,
    )

    # Task already completed by the current user
    task_1 = create_task_crud(
        TaskCreateDto(
            **{
                **task_data,
                "name": "task_1",
                "step_id": step.id,
                "status": Status.IN_PROGRESS,
                "redundancy": 1,
            }
        ),
        db_session,
    )

    # Task still available
    task_2 = create_task_crud(
        TaskCreateDto(
            **{
                **task_data,
                "name": "task_2",
                "step_id": step.id,
                "status": Status.IN_PROGRESS,
                "redundancy": 1,
            }
        ),
        db_session,
    )

    # User already completed task_1
    create_annotation_crud(
        db_session,
        AnnotationFullCreate(
            annotation={
                "user_email": "user.email@ina.fr",
                "annotation_status": Status.DONE,
                "version": 1,
                "result": {},
            },
            association={
                "annotation_id": 0,
                "task_id": task_1.id,
                "direction": InOutEnum.OUT,
            },
        ),
    )

    result = _get_relevant_tasks_for_projects(
        db_session,
        [project.id],
        "user.email@ina.fr",
    )

    assert project.id in result
    assert task_1.id not in result[project.id]
    assert result[project.id] == [task_2.id]
