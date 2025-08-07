"""Unit tests for Media services"""

# pylint: disable=redefined-outer-name
from sqlalchemy.orm import Session as SQLAlchemySession

from ina_ground_control.schemas.media_schemas import MediaCreate
from ina_ground_control.services.media_service import (
    create_media_crud,
    delete_media_crud,
    get_media_by_id,
    get_medias,
    update_media_crud,
)


def test_get_medias(db_session: SQLAlchemySession):
    media_data_1 = {"url": "url test", "type": "mp4"}

    media_data_2 = {"url": "url test2", "type": "mp4"}
    created_media_1 = create_media_crud(MediaCreate(**media_data_1), db_session)
    created_media_2 = create_media_crud(MediaCreate(**media_data_2), db_session)

    retrieved_medias = get_medias(db_session)

    assert retrieved_medias is not None
    assert retrieved_medias[0].id == created_media_1.id
    assert retrieved_medias[0].url == media_data_1["url"]
    assert retrieved_medias[0].type.value == media_data_1["type"]
    assert retrieved_medias[1].id == created_media_2.id
    assert retrieved_medias[1].url == media_data_2["url"]
    assert retrieved_medias[1].type.value == media_data_2["type"]


def test_create_media_crud(db_session: SQLAlchemySession):
    """
    Testing media creation service
    """
    media_data = {"url": "url test", "type": "mp4"}
    created_media = create_media_crud(MediaCreate(**media_data), db_session)
    assert created_media is not None
    assert created_media.id is not None
    assert created_media.url == media_data["url"]
    assert created_media.type.value == media_data["type"]


def test_get_media_by_id(db_session: SQLAlchemySession):
    media_data = {"url": "url test", "type": "mp4"}
    created_media = create_media_crud(MediaCreate(**media_data), db_session)

    retrieved_media = get_media_by_id(db_session, created_media.id)

    assert retrieved_media is not None
    assert retrieved_media.id == created_media.id
    assert retrieved_media.url == media_data["url"]
    assert retrieved_media.type.value == media_data["type"]


def test_get_media_by_inexistant_id(db_session: SQLAlchemySession):
    inexistant_media = get_media_by_id(db_session, 999)
    assert inexistant_media is None


def test_update_media_crud(db_session: SQLAlchemySession):
    media_data = {"url": "url test", "type": "mp4"}
    created_media = create_media_crud(MediaCreate(**media_data), db_session)
    updated_media_data = {"url": "url updated", "type": "hls"}
    update_media_crud(created_media.id, MediaCreate(**updated_media_data), db_session)
    retrieved_updated_media = get_media_by_id(db_session, created_media.id)

    assert retrieved_updated_media is not None
    assert retrieved_updated_media.url == updated_media_data["url"]
    assert retrieved_updated_media.type.value == updated_media_data["type"]


def test_delete_media_crud(db_session: SQLAlchemySession):
    media_data = {"url": "url test", "type": "hls"}
    created_media = create_media_crud(MediaCreate(**media_data), db_session)

    delete_media_crud(db_session, created_media.id)

    retrieved_media = get_media_by_id(db_session, created_media.id)

    assert created_media is not None
    assert retrieved_media is None
