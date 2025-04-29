"""Unit tests for Tag services"""
# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from ina_ground_control.database import Base
from ina_ground_control.schemas.tag_schemas import TagCreate
from ina_ground_control.services.tag_service import (
    get_tag_by_key,
    create_tag_crud,
    update_tag_crud,
    delete_tag_crud,
    get_tags,
)


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Mock the database using SQLite in memory.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """
    Create a session for each test to interact with the SQLite database.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_get_tags(test_db_session: SQLAlchemySession):
    tag_data_1 = {
        "key": "123",
        "value": "first tag",
        "project_id": 1,
    }
    tag_data_2 = {
        "key": "321",
        "value": "second tag",
        "project_id": 1,
    }
    created_tag_1 = create_tag_crud(TagCreate(**tag_data_1), test_db_session)
    created_tag_2 = create_tag_crud(TagCreate(**tag_data_2), test_db_session)

    retrieved_tags = get_tags(test_db_session)

    assert retrieved_tags is not None
    assert retrieved_tags[0].key == created_tag_1.key
    assert retrieved_tags[0].value == tag_data_1["value"]
    assert retrieved_tags[1].key == created_tag_2.key
    assert retrieved_tags[1].value == tag_data_2["value"]


def test_get_tag_by_key(test_db_session: SQLAlchemySession):
    tag_data = {
        "key": "124",
        "value": "first tag",
        "project_id": 1,
    }
    created_tag = create_tag_crud(TagCreate(**tag_data), test_db_session)
    retrieved_tag = get_tag_by_key(test_db_session, created_tag.key)

    assert retrieved_tag is not None
    assert retrieved_tag.key == tag_data["key"]
    assert retrieved_tag.value == tag_data["value"]


def test_create_tag_crud(test_db_session: SQLAlchemySession):
    """
    Test the tag creation service.
    """
    tag_data = {
        "key": "126",
        "value": "first tag",
        "project_id": 1,
    }

    retrieved_tag = get_tag_by_key(test_db_session, tag_data["key"])
    if retrieved_tag is None:
        created_tag = create_tag_crud(TagCreate(**tag_data), test_db_session)
        assert created_tag is not None
        assert created_tag.key is not None
        assert created_tag.key == tag_data["key"]
        assert created_tag.value == tag_data["value"]


def test_update_data_tag_crud(test_db_session: SQLAlchemySession):
    tag_data = {
        "key": "12",
        "value": "first tag",
        "project_id": 1,
    }
    create_tag_crud(TagCreate(**tag_data), test_db_session)
    updated_tag_data = {
        "key": "12",
        "value": "tag value",
        "project_id": 1,
    }
    update_tag_crud(tag_data["key"], TagCreate(**updated_tag_data), test_db_session)
    retrieved_updated_tag = get_tag_by_key(test_db_session, tag_data["key"])

    assert retrieved_updated_tag is not None
    assert retrieved_updated_tag.key == updated_tag_data["key"]
    assert retrieved_updated_tag.value == updated_tag_data["value"]


def test_delete_tag_crud(test_db_session: SQLAlchemySession):
    tag_data = {
        "key": "13",
        "value": "first tag",
        "project_id": 1,
    }
    created_tag = create_tag_crud(TagCreate(**tag_data), test_db_session)
    delete_tag_crud(test_db_session, created_tag.key)
    retrieved_tag = get_tag_by_key(test_db_session, created_tag.key)

    assert created_tag is not None
    assert retrieved_tag is None
