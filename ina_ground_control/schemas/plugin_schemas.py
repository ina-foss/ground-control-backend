"""
Define Pydantic schemas for plugin management.

This module includes schemas for:
- Plugin creation (`PluginCreate`).
- Plugin details with ID (`PluginWithIdDto`).
- Plugin configuration data (`ConfigData`).
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, JsonValue

from ina_ground_control.models.plugin.plugin_base import DataTypeEnum, PluginConfigType
from ina_ground_control.models.plugin_model import DisplayZone, TypePlugin


class ConfigData(BaseModel):
    """
    Configuration data (DTO) for plugin integration.

    This class defines the core connection and behavior parameters needed by
    a plugin to interact with its data source.

    Attributes:
        type (PluginConfigType): Specifies whether the plugin performs a POST-based
            search (e.g., ElasticSearch) or a GET-based search (e.g., Wikidata).
        data_source (str): The endpoint or URL used to query data.
        data_type (DataTypeEnum): The format of the expected data response.
            Currently, only 'json' is supported.
        token_url (str, optional): OAuth2 token endpoint URL, if authentication is required.
        client_id (str, optional): Client ID for OAuth2 authentication.
        client_secret (str, optional): Client secret for OAuth2 authentication.
    """

    type: PluginConfigType
    data_source: str
    data_type: DataTypeEnum
    # Auth fields
    token_url: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, extra="allow"
    )


class DisplayConfig(BaseModel):
    """
    DTO for plugin display configuration.

    Attributes:
        multiple_values (Optional[bool]): Whether multiple values can be selected.
        max_items (int): Maximum number of items to display.
        order (int): The display order of the plugin.
    """

    multiple_values: Optional[bool] = None
    max_items: Optional[int] = None
    order: Optional[int] = None
    main_plugin: Optional[bool] = False
    label: Optional[str] = None
    default_value: Optional[str] = None
    is_verifiable: Optional[bool] = False
    is_required: Optional[bool] = False
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, extra="allow"
    )


class PluginCreate(BaseModel):
    """
    DTO to create a plugin object.

    Attributes:
          name (str): The name of the plugin.
          type (TypePlugin): The type of the plugin (from `TypePlugin` enum).
          data_categories (str): Categories for the plugin's data.
          display_zone (DisplayZone): The display zone for the plugin.
          step_id (int): The ID of the step associated with the plugin.
          config_data (ConfigData): Configuration data for the plugin.
          display_config (Optional[DisplayConfig]): Optional display configuration.
          enable_search (Optional[bool]): Enable search feature for embedded plugins.
          data_property (Optional[str]): Data property reference for embedded plugins.
          children_plugins (Optional[List[PluginCreate]]): List of embedded child plugins.
    """

    name: str
    type: TypePlugin
    data_categories: str
    display_zone: DisplayZone
    step_id: int
    available_plugins: Optional[JsonValue] = None
    config_data: ConfigData
    display_config: Optional[DisplayConfig] = None
    # fields for embedded plugin
    enable_search: Optional[bool] = False
    data_property: Optional[str] = None
    children: Optional[List["PluginCreate"]] = []
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, extra="ignore"
    )


class PluginWithIdDto(PluginCreate):
    """
    Extends PluginCreate with an additional id field.

    Attributes:
        id (int): The unique identifier of the plugin.
    """

    id: int
    children: Optional[List["PluginWithIdDto"]] = []  # type: ignore[assignment]


PluginWithIdDto.model_rebuild()
PluginCreate.model_rebuild()
