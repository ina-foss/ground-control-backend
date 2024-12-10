from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


from ina_ground_control.models.plugin_model import TypePlugin,DisplayZone

class config_data(BaseModel):
    """
    DTO for the configuration data of a plugin.
    """
    type: str
    datasource: str

class PluginCreate(BaseModel):
    """
    DTO to create a plugin object
    """

    name: str
    type: TypePlugin
    data_categories: str
    display_zone : DisplayZone
    step_id: int
    config_data: config_data

    class Config:
        from_attributes = True


class PluginWithIdDto(PluginCreate):
    """
    Extends PluginCreate with an additional id field.
    """

    id: int