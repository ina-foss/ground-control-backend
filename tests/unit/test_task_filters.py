"""Unit tests for filtering, searching and paginating the tasks of a step."""

# pylint: disable=redefined-outer-name
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ina_ground_control.constants.enums import ExpirationFilter, InOutEnum, Status
from ina_ground_control.models import Base
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import AnnotationTask
from ina_ground_control.models.task_model import Task
from ina_ground_control.services.task_service import (
    count_tasks_by_step_crud,
    get_tasks_by_step_crud,
)

NOW = datetime.now(timezone.utc).replace(tzinfo=None)
PAST = NOW - timedelta(days=1)
FUTURE = NOW + timedelta(days=1)

# Distinct, strictly increasing creation dates for the 5 step-1 tasks.
CREATED_1 = NOW - timedelta(days=10)
CREATED_2 = NOW - timedelta(days=8)
CREATED_3 = NOW - timedelta(days=6)
CREATED_4 = NOW - timedelta(days=4)
CREATED_5 = NOW - timedelta(days=2)

# Distinct, strictly increasing update dates for the 5 step-1 tasks.
UPDATED_1 = NOW - timedelta(days=9)
UPDATED_2 = NOW - timedelta(days=7)
UPDATED_3 = NOW - timedelta(days=5)
UPDATED_4 = NOW - timedelta(days=3)
UPDATED_5 = NOW - timedelta(days=1)

# Annotation dates.
ANN_CREATED_EARLY = NOW - timedelta(days=10)
ANN_CREATED_MID = NOW - timedelta(days=6)
ANN_CREATED_LATE = NOW - timedelta(days=2)
ANN_UPDATED = NOW - timedelta(days=9)


@pytest.fixture()
def db_session():
    """Fresh in-memory SQLite session per test for isolation."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    _seed_tasks(session)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _seed_tasks(db: Session) -> None:
    """Seed step 1 with 5 tasks and step 2 with 1 task (to check isolation).

    Only "Alpha Test", "Beta TEST" and "Delta Test" carry the word "test"; the
    instruction/documentation keywords are deliberately distinct from it so the
    multi-field search can be asserted precisely.
    """
    tasks = [
        Task(
            name="Alpha Test",
            status=Status.DRAFT,
            expiration_date=PAST,
            created_at=CREATED_1,
            updated_at=UPDATED_1,
            step_id=1,
        ),
        Task(
            name="Beta TEST",
            status=Status.PENDING,
            expiration_date=FUTURE,
            created_at=CREATED_2,
            updated_at=UPDATED_2,
            step_id=1,
        ),
        Task(
            name="Gamma",
            status=Status.DONE,
            expiration_date=None,
            created_at=CREATED_3,
            updated_at=UPDATED_3,
            step_id=1,
            instruction="Annotate named entities",
        ),
        Task(
            name="Delta Test",
            status=Status.DRAFT,
            expiration_date=PAST,
            created_at=CREATED_4,
            updated_at=UPDATED_4,
            step_id=1,
        ),
        Task(
            name="Epsilon",
            status=Status.DONE,
            expiration_date=FUTURE,
            created_at=CREATED_5,
            updated_at=UPDATED_5,
            step_id=1,
            documentation="Transcription guidelines",
        ),
        Task(name="Other Test", status=Status.DRAFT, expiration_date=PAST, step_id=2),
    ]
    db.add_all(tasks)
    db.commit()
    _seed_annotations(db)


def _seed_annotations(db: Session) -> None:
    """Attach OUT annotations to some step-1 tasks (+ one IN, which must be ignored).

    - Alpha Test : alice / DONE, updated set
    - Beta TEST  : bob / IN_PROGRESS
    - Gamma      : alice / DONE
    - Delta Test : charlie / DONE but direction IN (never matched)
    - Epsilon    : no annotation
    """
    by_name = {t.name: t for t in db.query(Task).filter(Task.step_id == 1).all()}
    seeds = [
        (
            "Alpha Test",
            Annotation(
                user_email="alice@example.com",
                annotation_status=Status.DONE,
                version=1,
                created_at=ANN_CREATED_EARLY,
                updated_at=ANN_UPDATED,
            ),
            InOutEnum.OUT,
        ),
        (
            "Beta TEST",
            Annotation(
                user_email="bob@example.com",
                annotation_status=Status.IN_PROGRESS,
                version=1,
                created_at=ANN_CREATED_MID,
            ),
            InOutEnum.OUT,
        ),
        (
            "Gamma",
            Annotation(
                user_email="alice@example.com",
                annotation_status=Status.DONE,
                version=1,
                created_at=ANN_CREATED_LATE,
            ),
            InOutEnum.OUT,
        ),
        (
            "Delta Test",
            Annotation(
                user_email="charlie@example.com",
                annotation_status=Status.DONE,
                version=1,
                created_at=ANN_CREATED_MID,
            ),
            InOutEnum.IN,
        ),
    ]
    for name, annotation, direction in seeds:
        db.add(annotation)
        db.flush()
        db.add(
            AnnotationTask(
                annotation_id=annotation.id,
                task_id=by_name[name].id,
                direction=direction,
            )
        )
    db.commit()


# --------------------------------------------------------------------------- #
# Pagination / no filter                                                       #
# --------------------------------------------------------------------------- #
def test_pagination_without_filter(db_session: Session):
    # Only the tasks of step 1 are returned (isolation from step 2).
    assert count_tasks_by_step_crud(db_session, 1) == 5

    page_1 = get_tasks_by_step_crud(db_session, 1, skip=0, limit=2)
    page_2 = get_tasks_by_step_crud(db_session, 1, skip=2, limit=2)
    page_3 = get_tasks_by_step_crud(db_session, 1, skip=4, limit=2)

    assert [t.name for t in page_1] == ["Alpha Test", "Beta TEST"]
    assert len(page_2) == 2
    assert len(page_3) == 1
    assert {t.id for t in page_1}.isdisjoint({t.id for t in page_2})


def test_backward_compatible_call_without_filters(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, skip=0, limit=100)
    assert len(tasks) == 5
    assert all(t.step_id == 1 for t in tasks)


# --------------------------------------------------------------------------- #
# Exact search (SQL) across name / instruction / documentation                #
# --------------------------------------------------------------------------- #
def test_exact_search_on_name_is_partial_and_case_insensitive(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, search="test")

    assert {t.name for t in tasks} == {"Alpha Test", "Beta TEST", "Delta Test"}
    assert count_tasks_by_step_crud(db_session, 1, search="test") == 3


def test_exact_search_matches_instruction_field(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, search="entities")

    assert [t.name for t in tasks] == ["Gamma"]
    assert count_tasks_by_step_crud(db_session, 1, search="entities") == 1


def test_exact_search_matches_documentation_field(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, search="transcription")

    assert [t.name for t in tasks] == ["Epsilon"]
    assert count_tasks_by_step_crud(db_session, 1, search="transcription") == 1


def test_exact_search_restricted_to_search_fields(db_session: Session):
    # "entities" lives in Gamma.instruction.
    assert (
        get_tasks_by_step_crud(db_session, 1, search="entities", search_fields=["name"])
        == []
    )
    assert [
        t.name
        for t in get_tasks_by_step_crud(
            db_session, 1, search="entities", search_fields=["instruction"]
        )
    ] == ["Gamma"]

    # "test" lives only in names.
    assert (
        count_tasks_by_step_crud(
            db_session, 1, search="test", search_fields=["documentation"]
        )
        == 0
    )
    assert (
        count_tasks_by_step_crud(db_session, 1, search="test", search_fields=["name"])
        == 3
    )


def test_exact_search_invalid_field_raises(db_session: Session):
    with pytest.raises(ValueError, match="Invalid search field"):
        get_tasks_by_step_crud(db_session, 1, search="test", search_fields=["title"])


def test_fuzzy_search_restricted_to_search_fields(db_session: Session):
    common = dict(search="Transcirption guidlines", search_mode="fuzzy", min_score=70)

    # Restricted to documentation -> Epsilon matches.
    assert [
        t.name
        for t in get_tasks_by_step_crud(
            db_session, 1, **common, search_fields=["documentation"]
        )
    ] == ["Epsilon"]
    # Restricted to name -> no match.
    assert get_tasks_by_step_crud(db_session, 1, **common, search_fields=["name"]) == []


# --------------------------------------------------------------------------- #
# Fuzzy search (in memory) across name / instruction / documentation          #
# --------------------------------------------------------------------------- #
def test_fuzzy_search_tolerates_typos(db_session: Session):
    # "Transcirption guidlines" (typos) should still match Epsilon's documentation.
    tasks = get_tasks_by_step_crud(
        db_session,
        1,
        search="Transcirption guidlines",
        search_mode="fuzzy",
        min_score=70,
    )

    assert [t.name for t in tasks] == ["Epsilon"]


def test_fuzzy_search_count_matches_results(db_session: Session):
    kwargs = dict(search="Transcirption guidlines", search_mode="fuzzy", min_score=70)
    total = count_tasks_by_step_crud(db_session, 1, **kwargs)
    tasks = get_tasks_by_step_crud(db_session, 1, **kwargs)

    assert total == len(tasks) == 1


def test_fuzzy_search_pagination(db_session: Session):
    # A very permissive query returns several ranked results; pagination slices them.
    kwargs = dict(search="test", search_mode="fuzzy", min_score=50)
    total = count_tasks_by_step_crud(db_session, 1, **kwargs)
    page_1 = get_tasks_by_step_crud(db_session, 1, **kwargs, skip=0, limit=2)
    page_2 = get_tasks_by_step_crud(db_session, 1, **kwargs, skip=2, limit=2)

    assert total >= 3
    assert len(page_1) == 2
    assert {t.id for t in page_1}.isdisjoint({t.id for t in page_2})


def test_fuzzy_search_high_min_score_excludes_loose_matches(db_session: Session):
    # An unrelated query at a high threshold yields nothing.
    assert (
        count_tasks_by_step_crud(
            db_session, 1, search="zzzzzz", search_mode="fuzzy", min_score=90
        )
        == 0
    )


# --------------------------------------------------------------------------- #
# Structured filters                                                           #
# --------------------------------------------------------------------------- #
def test_filter_by_tasks_ids(db_session: Session):
    gamma = get_tasks_by_step_crud(db_session, 1, search="Gamma")[0]

    tasks = get_tasks_by_step_crud(db_session, 1, tasks_ids=[gamma.id])

    assert [t.id for t in tasks] == [gamma.id]
    assert count_tasks_by_step_crud(db_session, 1, tasks_ids=[gamma.id]) == 1


def test_filter_by_multiple_tasks_ids(db_session: Session):
    all_tasks = get_tasks_by_step_crud(db_session, 1)
    ids = [all_tasks[0].id, all_tasks[2].id]

    tasks = get_tasks_by_step_crud(db_session, 1, tasks_ids=ids)

    assert sorted(t.id for t in tasks) == sorted(ids)
    assert count_tasks_by_step_crud(db_session, 1, tasks_ids=ids) == 2


def test_filter_by_status(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, status=Status.DRAFT)

    assert {t.name for t in tasks} == {"Alpha Test", "Delta Test"}
    assert count_tasks_by_step_crud(db_session, 1, status=Status.DRAFT) == 2


def test_filter_expired(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.EXPIRED)

    assert {t.name for t in tasks} == {"Alpha Test", "Delta Test"}
    assert (
        count_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.EXPIRED)
        == 2
    )


def test_filter_active_includes_tasks_without_expiration(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.ACTIVE)

    assert {t.name for t in tasks} == {"Beta TEST", "Gamma", "Epsilon"}
    assert (
        count_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.ACTIVE) == 3
    )


def test_filter_all_applies_no_expiration_restriction(db_session: Session):
    assert count_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.ALL) == 5
    assert (
        len(get_tasks_by_step_crud(db_session, 1, expiration=ExpirationFilter.ALL)) == 5
    )


# --------------------------------------------------------------------------- #
# Creation-date filters                                                        #
# --------------------------------------------------------------------------- #
def test_filter_created_from_only_is_inclusive(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, created_from=CREATED_3)

    assert {t.name for t in tasks} == {"Gamma", "Delta Test", "Epsilon"}
    assert count_tasks_by_step_crud(db_session, 1, created_from=CREATED_3) == 3


def test_filter_created_to_only_is_inclusive(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, created_to=CREATED_3)

    assert {t.name for t in tasks} == {"Alpha Test", "Beta TEST", "Gamma"}
    assert count_tasks_by_step_crud(db_session, 1, created_to=CREATED_3) == 3


def test_filter_created_range_is_inclusive_on_both_bounds(db_session: Session):
    tasks = get_tasks_by_step_crud(
        db_session, 1, created_from=CREATED_2, created_to=CREATED_4
    )

    assert {t.name for t in tasks} == {"Beta TEST", "Gamma", "Delta Test"}
    assert (
        count_tasks_by_step_crud(
            db_session, 1, created_from=CREATED_2, created_to=CREATED_4
        )
        == 3
    )


# --------------------------------------------------------------------------- #
# Update-date filters                                                          #
# --------------------------------------------------------------------------- #
def test_filter_updated_from_only_is_inclusive(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, updated_from=UPDATED_3)

    assert {t.name for t in tasks} == {"Gamma", "Delta Test", "Epsilon"}
    assert count_tasks_by_step_crud(db_session, 1, updated_from=UPDATED_3) == 3


def test_filter_updated_to_only_is_inclusive(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, updated_to=UPDATED_3)

    assert {t.name for t in tasks} == {"Alpha Test", "Beta TEST", "Gamma"}
    assert count_tasks_by_step_crud(db_session, 1, updated_to=UPDATED_3) == 3


def test_filter_updated_range_is_inclusive_on_both_bounds(db_session: Session):
    tasks = get_tasks_by_step_crud(
        db_session, 1, updated_from=UPDATED_2, updated_to=UPDATED_4
    )

    assert {t.name for t in tasks} == {"Beta TEST", "Gamma", "Delta Test"}
    assert (
        count_tasks_by_step_crud(
            db_session, 1, updated_from=UPDATED_2, updated_to=UPDATED_4
        )
        == 3
    )


def test_created_and_updated_ranges_combine(db_session: Session):
    # created_from CREATED_3 (Gamma, Delta, Epsilon) AND updated_to UPDATED_4
    # (Alpha..Delta) -> intersection {Gamma, Delta Test}.
    tasks = get_tasks_by_step_crud(
        db_session, 1, created_from=CREATED_3, updated_to=UPDATED_4
    )

    assert {t.name for t in tasks} == {"Gamma", "Delta Test"}


# --------------------------------------------------------------------------- #
# Annotation filters (EXISTS on OUT annotations)                               #
# --------------------------------------------------------------------------- #
def test_filter_by_annotation_user_email(db_session: Session):
    tasks = get_tasks_by_step_crud(
        db_session, 1, annotation_user_email="alice@example.com"
    )

    assert {t.name for t in tasks} == {"Alpha Test", "Gamma"}
    assert (
        count_tasks_by_step_crud(
            db_session, 1, annotation_user_email="alice@example.com"
        )
        == 2
    )


def test_filter_by_annotation_status(db_session: Session):
    tasks = get_tasks_by_step_crud(db_session, 1, annotation_status=Status.IN_PROGRESS)

    assert [t.name for t in tasks] == ["Beta TEST"]
    assert (
        count_tasks_by_step_crud(db_session, 1, annotation_status=Status.IN_PROGRESS)
        == 1
    )


def test_in_direction_annotations_are_ignored_by_default(db_session: Session):
    # Default direction is OUT -> charlie's IN annotation must not match.
    assert (
        count_tasks_by_step_crud(
            db_session, 1, annotation_user_email="charlie@example.com"
        )
        == 0
    )


def test_filter_by_annotation_direction_in(db_session: Session):
    # charlie's annotation is direction IN -> matched only when asking for IN.
    tasks = get_tasks_by_step_crud(
        db_session,
        1,
        annotation_user_email="charlie@example.com",
        annotation_direction=InOutEnum.IN,
    )
    assert [t.name for t in tasks] == ["Delta Test"]
    assert (
        count_tasks_by_step_crud(
            db_session,
            1,
            annotation_user_email="charlie@example.com",
            annotation_direction=InOutEnum.IN,
        )
        == 1
    )


def test_annotation_direction_in_excludes_out_annotations(db_session: Session):
    # alice's annotations are OUT -> asking for IN yields nothing.
    assert (
        get_tasks_by_step_crud(
            db_session,
            1,
            annotation_user_email="alice@example.com",
            annotation_direction=InOutEnum.IN,
        )
        == []
    )


def test_annotation_filters_apply_to_a_single_annotation(db_session: Session):
    # alice's annotations are DONE, so alice + IN_PROGRESS matches no single annotation.
    tasks = get_tasks_by_step_crud(
        db_session,
        1,
        annotation_user_email="alice@example.com",
        annotation_status=Status.IN_PROGRESS,
    )
    assert tasks == []


def test_filter_by_annotation_created_range(db_session: Session):
    # Only Gamma's annotation was created at/after ANN_CREATED_LATE.
    tasks = get_tasks_by_step_crud(
        db_session, 1, annotation_created_from=ANN_CREATED_LATE
    )
    assert [t.name for t in tasks] == ["Gamma"]


def test_filter_by_annotation_updated_range(db_session: Session):
    # Only Alpha's annotation has updated_at set.
    tasks = get_tasks_by_step_crud(db_session, 1, annotation_updated_from=ANN_UPDATED)
    assert [t.name for t in tasks] == ["Alpha Test"]


def test_annotation_filter_combines_with_task_filter(db_session: Session):
    # annotation DONE (Alpha, Gamma) AND task status DRAFT (Alpha, Delta) -> Alpha.
    tasks = get_tasks_by_step_crud(
        db_session, 1, status=Status.DRAFT, annotation_status=Status.DONE
    )
    assert [t.name for t in tasks] == ["Alpha Test"]


# --------------------------------------------------------------------------- #
# Cumulative filters                                                           #
# --------------------------------------------------------------------------- #
def test_combined_filters_are_cumulative(db_session: Session):
    # search=test AND active -> only "Beta TEST" (future); the two past ones excluded.
    tasks = get_tasks_by_step_crud(
        db_session, 1, search="test", expiration=ExpirationFilter.ACTIVE
    )

    assert [t.name for t in tasks] == ["Beta TEST"]
    assert (
        count_tasks_by_step_crud(
            db_session, 1, search="test", expiration=ExpirationFilter.ACTIVE
        )
        == 1
    )


def test_search_combines_with_created_range(db_session: Session):
    # status=DRAFT (Alpha, Delta) AND created_to=CREATED_2 -> only Alpha (Delta later).
    tasks = get_tasks_by_step_crud(
        db_session, 1, status=Status.DRAFT, created_to=CREATED_2
    )

    assert [t.name for t in tasks] == ["Alpha Test"]


def test_no_result(db_session: Session):
    assert get_tasks_by_step_crud(db_session, 1, tasks_ids=[999999]) == []
    assert count_tasks_by_step_crud(db_session, 1, tasks_ids=[999999]) == 0
