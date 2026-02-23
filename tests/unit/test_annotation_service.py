import logging
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from ina_ground_control.constants.enums import Status as AnnotationStatus
from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.services.annotation_service import (
    finish_annotation_crud,
    get_all_annotations_crud,
    get_annotations_by_id_crud,
    get_annotations_by_task_id_crud,
    skip_annotation_crud,
    udpate_annotation_result_crud,
)

# --------------------------------------------------------------------
# 1️⃣ Test get_annotations_by_task_id_crud for edge cases
# --------------------------------------------------------------------


def test_get_annotations_by_task_id_crud_no_results(db_session: Session):
    """
    Should return empty list if task_id doesn't exist
    """
    results = get_annotations_by_task_id_crud(
        db_session, task_id=9999, user_email=None, direction=InOutEnum.IN
    )
    assert results == []


def test_get_annotations_by_task_id_crud_empty_email(db_session: Session):
    """
    Should not filter if user_email is empty string
    """
    results = get_annotations_by_task_id_crud(
        db_session, task_id=1, user_email="", direction=InOutEnum.IN
    )
    assert isinstance(results, list)


# --------------------------------------------------------------------
# 2️⃣ Test udpate_annotation_result_crud error case
# --------------------------------------------------------------------


def test_update_annotation_result_crud_not_found(db_session: Session):
    """
    Should raise exception if annotation does not exist
    """
    with pytest.raises(GroundControlException):
        udpate_annotation_result_crud(db_session, {"bad": "data"}, annotation_id=9999)


# --------------------------------------------------------------------
# 3️⃣ Test skip_annotation_crud for not found
# --------------------------------------------------------------------


def test_skip_annotation_crud_not_found(db_session: Session):
    """
    Should raise exception if annotation not found
    """
    with pytest.raises(GroundControlException):
        skip_annotation_crud(db_session, 9999, "admin@localhost.com")


# --------------------------------------------------------------------
# 4️⃣ Test finish_annotation_crud for not found
# --------------------------------------------------------------------


def test_finish_annotation_crud_not_found(db_session: Session):
    """
    Should raise exception if annotation not found
    """
    with pytest.raises(GroundControlException):
        finish_annotation_crud(db_session, {"dummy": "result"}, annotation_id=9999)


# --------------------------------------------------------------------
# 5️⃣ Test get_annotations_by_id_crud logging error path
# --------------------------------------------------------------------


def test_get_annotations_by_id_crud_logs_error(db_session: Session, caplog):
    """
    Should log an error and raise exception if annotation not found
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(GroundControlException):
            get_annotations_by_id_crud(db_session, 9999)
    assert "Failed to retrieve annotation" in caplog.text


# --------------------------------------------------------------------
# 6️⃣ Test get_all_annotations_crud variations (date filters, pagination, etc.)
# --------------------------------------------------------------------


def test_get_all_annotations_crud_no_filters(db_session: Session):
    results = get_all_annotations_crud(db_session)
    assert isinstance(results, list)


@pytest.mark.parametrize(
    "start,end",
    [
        (datetime(2025, 4, 17, 8, 0, 0), None),
        (None, datetime(2025, 4, 17, 10, 0, 0)),
        (datetime(2025, 4, 17, 8, 0, 0), datetime(2025, 4, 17, 10, 0, 0)),
    ],
)
def test_get_all_annotations_crud_created_at_filters(db_session: Session, start, end):
    results = get_all_annotations_crud(
        db_session, start_created_at=start, end_created_at=end
    )
    assert isinstance(results, list)


@pytest.mark.parametrize(
    "start,end",
    [
        (datetime(2025, 4, 17, 8, 0, 0), None),
        (None, datetime(2025, 4, 17, 10, 0, 0)),
        (datetime(2025, 4, 17, 8, 0, 0), datetime(2025, 4, 17, 10, 0, 0)),
    ],
)
def test_get_all_annotations_crud_updated_at_filters(db_session: Session, start, end):
    results = get_all_annotations_crud(
        db_session, start_updated_at=start, end_updated_at=end
    )
    assert isinstance(results, list)


@pytest.mark.parametrize(
    "start,end",
    [
        (datetime(2025, 4, 17, 8, 0, 0), None),
        (None, datetime(2025, 4, 17, 10, 0, 0)),
        (datetime(2025, 4, 17, 8, 0, 0), datetime(2025, 4, 17, 10, 0, 0)),
    ],
)
def test_get_all_annotations_crud_validated_at_filters(db_session: Session, start, end):
    results = get_all_annotations_crud(
        db_session, start_validated_at=start, end_validated_at=end
    )
    assert isinstance(results, list)


def test_get_all_annotations_crud_with_pagination(db_session: Session):
    results = get_all_annotations_crud(db_session, skip=0, limit=2)
    assert isinstance(results, list)
    assert len(results) <= 2


def test_get_all_annotations_crud_with_status_and_email(db_session: Session):
    results = get_all_annotations_crud(
        db_session, status=AnnotationStatus.IN_PROGRESS, user_email="user.email@ina.fr"
    )
    assert all(isinstance(r.annotation_status, AnnotationStatus) for r in results)
