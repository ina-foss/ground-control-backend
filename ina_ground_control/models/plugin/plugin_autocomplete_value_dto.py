"""
Module plugin_autocomplete_value_dto.

This module defines the PluginAutocompleteValueDTO class, a data transfer object (DTO)
used to represent autocomplete values for plugins. It includes optional attributes for
an internal ID, an external ID, and a label.

Classes:
    PluginAutocompleteValueDTO: A Pydantic BaseModel representing plugin autocomplete values.
        Attributes:
            id (Optional[str]): The internal identifier for the plugin autocomplete value.
            ext_id (Optional[str]): The external identifier for the plugin autocomplete value.
            label (Optional[str]): The display label for the plugin autocomplete value.
"""
from typing import Optional
from pydantic import BaseModel

class PluginAutocompleteValueDTO(BaseModel):
    id: Optional[str]
    ext_id: Optional[str]
    label: Optional[str]
