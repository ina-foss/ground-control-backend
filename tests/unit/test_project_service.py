"""Unit tests for Project services"""

import pytest
from sqlalchemy.orm import Session as SQLAlchemySession

from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.project_model import ProjectStatus
from ina_ground_control.models.step_model import StepStatus
from ina_ground_control.models.task_model import TaskStatus
from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.schemas.task_schemas import TaskWithIdDto
from ina_ground_control.services.project_service import (
    create_project_crud,
    delete_project_crud,
    finish_project_service,
    get_progressed_tasks_for_project_service,
    get_project_by_id,
    get_projects,
    update_project_crud,
)

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


def test_get_projects(db_session: SQLAlchemySession):
    """
    Test to retrieve all the projects in the database
    """
    project_data_1 = {
        "title": "Test Project 1",
        "description": "Test description 1",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "john@example.com",
    }
    project_data_2 = {
        "title": "Test Project 2",
        "description": "Test description 2",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "jane@example.com",
    }

    created_project_1 = create_project_crud(
        db_session, ProjectBaseDto(**project_data_1)
    )
    created_project_2 = create_project_crud(
        db_session, ProjectBaseDto(**project_data_2)
    )

    retrieved_projects = get_projects(db_session)

    # Ensure at least 2 projects were returned
    assert len(retrieved_projects) >= 2

    # Find the created projects in the returned list dynamically
    project_1 = next(p for p in retrieved_projects if p.id == created_project_1.id)
    project_2 = next(p for p in retrieved_projects if p.id == created_project_2.id)

    assert project_1.title == project_data_1["title"]
    assert project_1.description == project_data_1["description"]
    assert project_1.created_by == project_data_1["created_by"]

    assert project_2.title == project_data_2["title"]
    assert project_2.description == project_data_2["description"]
    assert project_2.created_by == project_data_2["created_by"]


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
    """
    Test update a project attributes (title, description and author)
    """
    created_project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    updated_task_data = {
        "title": "Test Project 2",
        "description": "Test description 2",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "jane@example.com",
    }
    update_project_crud(
        db_session, ProjectBaseDto(**updated_task_data), created_project.id
    )

    retrieved_updated_project = get_project_by_id(db_session, created_project.id)

    assert retrieved_updated_project is not None
    assert retrieved_updated_project.title == updated_task_data["title"]
    assert retrieved_updated_project.description == updated_task_data["description"]
    assert retrieved_updated_project.created_by == updated_task_data["created_by"]


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
            task.status = TaskStatus.DRAFT
    db_session.commit()
    finish_project_service(db_session, project.id)
    retrieved_project = get_project_by_id(db_session, project.id)
    assert retrieved_project.status == ProjectStatus.DONE
    for step in retrieved_project.steps:
        assert step.status == StepStatus.DONE
        for task in step.tasks:
            assert task.status == TaskStatus.DONE


def test_get_progressed_tasks_for_project_service(db_session: SQLAlchemySession):
    """
    Test that get_progressed_tasks_for_project_service returns only tasks
    with IN_PROGRESS status for a given project.
    """
    task_status = TaskStatus.DONE
    project = create_project_crud(db_session, ProjectBaseDto(**project_data))

    for step in project.steps:
        for task in step.tasks:
            task.status = task_status
    db_session.commit()

    if task_status == TaskStatus.IN_PROGRESS:
        tasks = get_progressed_tasks_for_project_service(db_session, project.id)
        assert isinstance(tasks, list)
        assert all(isinstance(t, TaskWithIdDto) for t in tasks)
        for t in tasks:
            assert t.status == TaskStatus.IN_PROGRESS
    else:
        tasks = get_progressed_tasks_for_project_service(db_session, project.id)
        assert tasks == []


def test_get_progressed_tasks_for_nonexistent_project(db_session: SQLAlchemySession):
    """
    Test that requesting in-progress tasks for a nonexistent project
    raises GroundControlException with RESOURCE_NOT_FOUND.
    """
    non_existing_project_id = 9999
    with pytest.raises(GroundControlException) as exc_info:
        get_progressed_tasks_for_project_service(db_session, non_existing_project_id)
    assert exc_info.value.code == ErrorCode.RESOURCE_NOT_FOUND.value[0]
