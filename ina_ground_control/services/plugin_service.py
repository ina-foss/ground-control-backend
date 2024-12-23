"""
This module provides CRUD operations for plugins.

It includes functions to retrieve a plugins by ID_step and name.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.plugin_model import Plugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate
from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_config import PluginConfigDTO
from ina_ground_control.services.plugins.plugin_service_autocomplete import PluginServiceAutoComplete


def get_plugins_search(db: Session, plugin_id: int, query: str):
    plugin = get_plugin_by_id(db, plugin_id)
    result = PluginConfigDTO.build(plugin.config_data)
    result = PluginConfigAutoComplete(**result)
    print(f"test: {isinstance(result, PluginConfigAutoComplete)}")
    print(f"test1: {type(result).__name__}")
    print(f"test1: {plugin.config_data}")
    if isinstance(result, PluginConfigAutoComplete):
        plugin = PluginServiceAutoComplete(plugin.config_data)
        return plugin.search(query)
    else:
        raise NotImplementedError(f'{str(result)} not implemented')


def create_plugin_crud(plugin: PluginCreate, db: Session):
    """
    Create a new plugin in the database.

    Attributes:
        plugin (PluginCreate): The step data transfer object containing plugin details.
        db (Session): The database session used for querying.

    Returns:
        Plugin: The newly created Plugin object.
    """
    db_plugin = Plugin(**plugin.model_dump())
    db.add(db_plugin)
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

def get_plugins_crud(db: Session, step_id:int, plugin_type:str,zone:str):

    return db.query(Plugin).filter(Plugin.step_id == step_id,Plugin.type == plugin_type,
                                    Plugin.display_zone == zone).all()


def get_plugin_by_id(db: Session, plugin_id: int):
    """
    Retrieve a plugin by its ID

    Parameters:
    db (Session): The database session used for querying.
    plugin_id (int): The unique identifier of the plugin to retrieve.

    Returns:
    Plugin: The Plugin object if found, otherwise None.
    """
    return db.query(Plugin).filter(Plugin.id == plugin_id).first()
def delete_plugin_crud(db: Session, plugin_id: int):
    """
    Delete a plugin from the database.

    Parameters:
    db (Session): The database session used for querying.
    plugin_id (int): The unique identifier of the plugin to delete.

    Returns:
    Plugin: The deleted Plugin object if the project exists, otherwise None.
    """
    db_plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if db_plugin is not None:
        db.delete(db_plugin)
        db.commit()
    return db_plugin
