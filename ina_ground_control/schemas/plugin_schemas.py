from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


from ina_ground_control.models.plugin_model import TypePlugin


class PluginCreate(BaseModel):
    """
    DTO to create a plugin object
    """

    name: str
    type: TypePlugin
    step_id : int
    configData : {}

    class Config:
        from_attributes = True


class PluginWithIdDto(PluginCreate):
    """
    Extends PluginCreate with an additional id field.
    """

    id: int