"""Unit tests for plugin serialization"""

# pylint: disable=redefined-outer-name
import pytest
from pydantic import ValidationError

from ina_ground_control.models.plugin.plugin_autocomplete import (
    PluginConfigAutoComplete,
)
from ina_ground_control.models.plugin.plugin_base import (
    DataTypeEnum,
    PluginConfigBase,
    PluginConfigType,
)
from ina_ground_control.models.plugin.plugin_config import PluginConfigDTO


def test_plugin_config_base_valid_type():
    data1 = {
        "type": PluginConfigType.GET_PLUGIN,
        "data_type": DataTypeEnum.JSON,
        "data_source": "https://cv.iptc.org/newscodes/mediatopic?lang=fr",
        "search_query": "title",
        "response_id_key": "$.conceptSet[:1].prefLabel.fr",
        "response_ext_id_key": "$.conceptSet[:1].prefLabel.fr",
        "response_label_key": "$.conceptSet[:1].prefLabel.fr",
    }

    config = PluginConfigDTO.build(data1)
    assert isinstance(config, PluginConfigAutoComplete)

    assert isinstance(config, PluginConfigAutoComplete)
    assert config.type == PluginConfigType.GET_PLUGIN
    assert config.data_source == "https://cv.iptc.org/newscodes/mediatopic?lang=fr"


def test_plugin_config_base_invalid_type():
    data = {"type": "unknown-type", "data_source": "some_data_source"}
    config = PluginConfigDTO.build(data)
    assert config["type"] == "unknown-type"
    assert config["data_source"] == "some_data_source"


def test_plugin_config_base_missing_type():
    data = {"data_source": "some_data_source"}
    with pytest.raises(ValidationError):
        PluginConfigBase(**data)


def test_plugin_config_base_extra_fields():
    data = {
        "type": PluginConfigType.GET_PLUGIN,
        "data_type": DataTypeEnum.JSON,
        "data_source": "https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
        "search_query": "title",
        "response_id_key": "id",
        "response_ext_id_key": "code",
        "response_label_key": "label",
    }
    config = PluginConfigDTO.build(data)
    assert isinstance(config, PluginConfigAutoComplete)
    assert config.type == PluginConfigType.GET_PLUGIN
    assert (
        config.data_source
        == "https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json"
    )
    assert not hasattr(
        config, "extra_field"
    )  # Must not have extra fields if extra='ignore'
