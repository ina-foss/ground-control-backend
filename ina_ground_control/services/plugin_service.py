"""
This module provides CRUD operations for plugins.

It includes functions to retrieve a plugins by ID_step and name.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.plugin_model import Plugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate
def get_plugins(db: Session, step_id: int,name:str):
    plugins = (
        db.query(Plugin)
        .filter(Plugin.step_id == step_id)
        .filter(Plugin.name.ilike(f"%{name}%"))
        .filter(Plugin.type == "autocomplete")
        .all()
    )
    return plugins