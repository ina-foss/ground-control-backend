"""Unit tests for Plugin services"""

# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy.orm import Session as SQLAlchemySession

from ina_ground_control.models.plugin.plugin_base import DataTypeEnum, PluginConfigType
from ina_ground_control.models.plugin_model import DisplayZone, TypePlugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate
from ina_ground_control.services.plugin_service import (
    create_plugin_crud,
    delete_plugin_crud,
    get_plugin_by_id,
    get_plugins_crud,
    get_plugins_search,
)

plugin_data = {
    "name": "name_test",
    "type": TypePlugin.AUTOCOMPLETE,
    "data_categories": "data_categories test",
    "display_zone": DisplayZone.BLOC,
    "step_id": 1,
    "config_data": {
        "type": PluginConfigType.PLUGIN_REQUEST_GET,
        "data_type": DataTypeEnum.JSON,
        "data_source": "test data",
    },
}


def test_get_plugins(db_session: SQLAlchemySession):
    plugin_1 = {
        "name": "name_test",
        "type": TypePlugin.LIST_ITEMS,
        "data_categories": "data_categories test",
        "display_zone": DisplayZone.BLOC,
        "step_id": 1,
        "config_data": {
            "type": PluginConfigType.PLUGIN_STATIC_DATA,
            "data_type": DataTypeEnum.JSON,
            "data_source": '[{"id":1,"extId":"A1","label":"Item 1"},{"id":2,"extId":"A2","label":"Item 2"}]',
            "search_query": "",
            "response_id_key": "$[*].id",
            "response_ext_id_key": "$[*].code",
            "response_label_key": "$[*].label",
        },
    }
    created_plugin_1 = create_plugin_crud(PluginCreate(**plugin_1), db_session)
    assert created_plugin_1 is not None
    db_session.commit()
    db_session.refresh(created_plugin_1)
    given_plugin = get_plugin_by_id(db_session, 1)
    assert given_plugin is not None
    assert given_plugin.id is not None
    assert given_plugin.id == 1
    retrieved_plugins = get_plugins_search(db_session, 1, "Item")
    assert retrieved_plugins is not None


def test_create_plugin_crud(db_session: SQLAlchemySession):
    created_plugin = create_plugin_crud(PluginCreate(**plugin_data), db_session)
    assert created_plugin is not None
    assert created_plugin.id is not None
    assert created_plugin.name == plugin_data["name"]
    assert created_plugin.type == plugin_data["type"]
    assert created_plugin.data_categories == plugin_data["data_categories"]
    assert created_plugin.display_zone == plugin_data["display_zone"]
    assert created_plugin.step_id == plugin_data["step_id"]


def test_delete_plugin_crud(db_session: SQLAlchemySession):
    """
    Test the deletion of a plugin given its id
    """
    plugin_1 = {
        "name": "name_test",
        "type": TypePlugin.AUTOCOMPLETE,
        "data_categories": "data_categories test",
        "display_zone": DisplayZone.BLOC,
        "step_id": 1,
        "config_data": {
            "data_source": "test data",
            "type": PluginConfigType.PLUGIN_REQUEST_GET,
            "data_type": DataTypeEnum.JSON,
        },
    }
    created_plugin = create_plugin_crud(PluginCreate(**plugin_1), db_session)

    getted_plugin = get_plugins_crud(
        db_session, created_plugin.id, created_plugin.type, created_plugin.display_zone
    )
    assert getted_plugin is not None

    delete_plugin_crud(db_session, created_plugin.id)

    retrieved_plugin = get_plugin_by_id(db_session, created_plugin.id)

    assert created_plugin is not None
    assert retrieved_plugin is None


def test_get_plugin_by_id_not_found(db_session: SQLAlchemySession):
    """Should return None if plugin ID not found"""
    result = get_plugin_by_id(db_session, 9999)
    assert result is None


def test_delete_plugin_crud_not_found(db_session: SQLAlchemySession):
    """Should return None if plugin doesn't exist"""
    result = delete_plugin_crud(db_session, 9999)
    assert result is None


def test_get_plugins_crud_zone_str(db_session: SQLAlchemySession):
    """Should return plugins filtered by string zone"""
    result = get_plugins_crud(db_session, step_id=1, zone=DisplayZone.BLOC)
    assert isinstance(result, list)


def test_get_plugins_crud_zone_list(db_session: SQLAlchemySession):
    """Should return plugins filtered by list of zones"""
    result = get_plugins_crud(db_session, step_id=1, zone=[DisplayZone.BLOC])
    assert isinstance(result, list)
