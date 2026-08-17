"""Unit tests for typed step settings (creation, update and backward compat)."""

# pylint: disable=redefined-outer-name
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ina_ground_control.constants.enums import AnnotationType, LaunchMode, SpanMode
from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models import Base
from ina_ground_control.models.step_model import Step
from ina_ground_control.schemas.step_schemas import StepCreate
from ina_ground_control.services.step_service import (
    create_step_crud,
    get_step_by_id,
    update_step_settings_crud,
)


@pytest.fixture()
def db_session():
    """Fresh in-memory SQLite session per test for isolation."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _step_payload(annotation_type: AnnotationType, **overrides) -> dict:
    payload = {
        "title": "a step",
        "description": "",
        "annotation_type": annotation_type,
        "status": "draft",
        "pinned_at": None,
        "project_id": 1,
    }
    payload.update(overrides)
    return payload


def test_create_span_without_settings_uses_defaults(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.SPAN)), db_session
    )

    assert step.settings["mode"] == SpanMode.MONO.value
    assert step.settings["comments"] is True
    assert step.settings["display"]["span"] is True
    assert (
        step.settings["synchronization"]["launch_mode"] == LaunchMode.CTRL_CLICK.value
    )


def test_create_span_with_partial_settings_completes_defaults(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.SPAN, settings={"mode": "multi"})),
        db_session,
    )

    # Provided value is kept ...
    assert step.settings["mode"] == "multi"
    # ... and every missing field is filled with the SPAN defaults.
    assert step.settings["display"]["tc_bloc"] is True
    assert step.settings["synchronization"]["before_word"] == 2
    assert step.settings["comments"] is True


def test_create_video_segmentation_defaults(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.VIDEO_SEGMENTATION)), db_session
    )

    assert step.settings["display"]["tc_bloc"] is True
    assert step.settings["display"]["segment_number"] is False
    assert "synchronization" in step.settings


def test_create_auto_summary_has_no_display_or_sync(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.AUTO_SUMMARY)), db_session
    )

    # Auto summary exposes no display / synchronization / comment settings.
    assert step.settings == {}


def test_update_step_settings(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.SPAN)), db_session
    )

    updated = update_step_settings_crud(
        db_session, step.id, {"mode": "multi", "comments": False}
    )

    assert updated.settings["mode"] == "multi"
    assert updated.settings["comments"] is False
    # Untouched fields are still completed with the defaults.
    assert updated.settings["display"]["span"] is True


def test_update_step_settings_rejects_invalid_value(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.SPAN)), db_session
    )

    with pytest.raises(ValidationError):
        update_step_settings_crud(db_session, step.id, {"mode": "not-a-mode"})


def test_update_step_settings_rejects_unknown_key(db_session: Session):
    step = create_step_crud(
        StepCreate(**_step_payload(AnnotationType.SPAN)), db_session
    )

    with pytest.raises(ValidationError):
        update_step_settings_crud(db_session, step.id, {"unknown_field": True})


def test_update_settings_on_missing_step_raises(db_session: Session):
    with pytest.raises(GroundControlException):
        update_step_settings_crud(db_session, 9999, {"mode": "mono"})


def test_read_legacy_step_with_incomplete_settings(db_session: Session):
    """Old steps persisted with a null/partial settings blob must stay readable."""
    legacy = Step(
        title="legacy",
        description="",
        annotation_type=AnnotationType.SPAN,
        status="draft",
        project_id=1,
        settings=None,
    )
    db_session.add(legacy)
    db_session.commit()
    db_session.refresh(legacy)

    fetched = get_step_by_id(db_session, legacy.id)
    assert fetched.settings is None

    # And its settings can be repaired/normalized through the update route.
    repaired = update_step_settings_crud(db_session, legacy.id, {})
    assert repaired.settings["display"]["span"] is True
