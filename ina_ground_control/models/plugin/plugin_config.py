from typing import Type

from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase

# Ensure TYPE_MAPPING remains consistent
TYPE_MAPPING = {
    "plugin_autocomplete": PluginConfigAutoComplete,
}


class PluginConfigDTO():
    @staticmethod
    def build(values):
        type_field = values.get("type")
        if not type_field:
            raise ValueError('The "type" field is required to determine the correct subtype.')
        if type_field in TYPE_MAPPING:
            target_class: Type[PluginConfigBase] = TYPE_MAPPING[type_field]
            return target_class.model_validate(values)
        return values
