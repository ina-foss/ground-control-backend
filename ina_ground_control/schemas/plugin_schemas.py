"""
Define Pydantic schemas for plugin management.

This module includes schemas for:
- Plugin creation (`PluginCreate`).
- Plugin details with ID (`PluginWithIdDto`).
- Plugin configuration data (`ConfigData`).
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict

from ina_ground_control.models.plugin_model import TypePlugin, DisplayZone


class ConfigData(BaseModel):
    """
   DTO for the configuration data of a plugin.

   Attributes:
       type (str): The type of the plugin configuration.
       data_source (str): The datasource URL for the plugin.
   """
    type: str
    data_source: str
    data_type: str
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='allow'
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
  """

    name: str
    type: TypePlugin
    data_categories: str
    display_zone: DisplayZone
    step_id: int
    config_data: ConfigData

    # Use ConfigDict for configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='ignore'
    )


class PluginWithIdDto(PluginCreate):
    """
   Extends PluginCreate with an additional id field.

   Attributes:
       id (int): The unique identifier of the plugin.
   """

    id: int
