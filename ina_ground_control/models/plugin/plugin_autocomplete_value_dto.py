"""
Module plugin_autocomplete_value_dto.

This module defines the PluginAutocompleteValueDTO class, a data transfer object (DTO)
used to represent autocomplete values for plugins.
"""

from typing import Optional

from pydantic import BaseModel


class PluginAutocompleteValueDTO(BaseModel):
    """
    Data Transfer Object representing a plugin autocomplete value.

    Attributes:
        id (Optional[str | int]): Internal identifier.
        ext_id (Optional[str]): External identifier.
        label (Optional[str]): Display label.
        tag_label (Optional[str]): Alternative label used for tagging.
        link (Optional[str]): External URL associated with the value.
        image (Optional[str]): URL of the image displayed next to the option.
        description (Optional[str]): Additional descriptive information.
        categories (Optional[str]): Stringified JSON array of categories.
        group (Optional[str]): Group name for visual grouping in UI.
        editable (Optional[str]): Indicates if the value is editable.
        copyable (Optional[str]): Indicates if the value is copyable.
        tooltip (Optional[str]): Tooltip text displayed in UI.
    """

    id: Optional[str | int] = None
    ext_id: Optional[str] = None
    label: Optional[str] = None
    tag_label: Optional[str] = None
    link: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[str] = None
    group: Optional[str] = None
    editable: Optional[str] = None
    copyable: Optional[str] = None
    tooltip: Optional[str] = None
