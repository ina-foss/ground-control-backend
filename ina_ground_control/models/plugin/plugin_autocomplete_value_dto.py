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
            image (Optional[str]): Url of the image that should be display next to the option.
            description(Optional[str]): Additional information to describe the option.
            categories(Optional[str]): Stringified JSON array that may contains different categories.
            group(Optional[str]): Optional property to visually group the options in the plugin.
"""

from typing import Optional

from pydantic import BaseModel


class PluginAutocompleteValueDTO(BaseModel):
    id: Optional[str | int] = None
    ext_id: Optional[str] = None
    label: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[str] = None
    group: Optional[str] = None
    editable: Optional[str] = None
    copyable: Optional[str] = None
