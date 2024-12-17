import pytest
from pydantic import ValidationError

from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase
from ina_ground_control.models.plugin.plugin_config import PluginConfigDTO


def test_plugin_config_base_valid_type():
    data = {
        "type": "plugin_autocomplete",
        "data_source": "some_data_source",
        "search_attr": "title",
        "search_query_param": "q",
        "search_item_size": 30,
        "search_item_sort": "title,asc"
    }
    data1 = {
        "type": "plugin_autocomplete",
        "data_type": "json",
        "data_source": "https://cv.iptc.org/newscodes/mediatopic?lang=fr",
        "response_id_key": "$.conceptSet[:1].prefLabel.fr",
        "response_ext_id_key": "$.conceptSet[:1].prefLabel.fr",
        "response_label_key": "$.conceptSet[:1].prefLabel.fr"
    }
    data = {
        "type": "plugin_autocomplete",
        "data_type": "json",
        "data_source": "https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
        "response_id_key": "id",
        "response_ext_id_key": "code",
        "response_label_key": "label"
    }

    try:
        config = PluginConfigDTO.build(data)
        assert isinstance(config, PluginConfigAutoComplete)
    except ValidationError as e:
        print("Validation error occurred:")
        for error in e.errors():
            print(f"Field: {error['loc']}")
            print(f"Error: {error['msg']}")
            print(f"Type: {error['type']}")

    assert isinstance(config, PluginConfigAutoComplete)
    assert config.type == "plugin_autocomplete"
    assert config.data_source == "some_data_source"


def test_plugin_config_base_invalid_type():
    data = {
        "type": "unknown-type",
        "data_source": "some_data_source"
    }
    config = PluginConfigDTO.build(data)
    assert config["type"] == "unknown-type"
    assert config["data_source"] == "some_data_source"


def test_plugin_config_base_missing_type():
    data = {
        "data_source": "some_data_source"
    }
    with pytest.raises(ValidationError):
        PluginConfigBase(**data)


def test_plugin_config_base_extra_fields():
    data = {
        "type": "plugin_autocomplete",
        "data_source": "some_data_source",
        "extra_field": "extra_value",
        "search_attr": "title",
        "search_query_param": "q",
        "search_item_size": 30,
        "search_item_sort": "title,asc"
    }
    config = PluginConfigDTO.build(data)
    assert isinstance(config, PluginConfigAutoComplete)
    assert config.type == "plugin_autocomplete"
    assert config.data_source == "some_data_source"
    assert not hasattr(config, 'extra_field')  # Must not have extra fields if extra='ignore'




