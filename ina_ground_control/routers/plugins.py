"""
Module: plugin_router

Description:
This module defines the routes for managing plugins within the FastAPI application.

Features:
- Search for plugins associated with a specific step and name.
- Handle exceptions when no matching plugins are found.
- Use dependencies to manage database sessions.

Endpoint:
- GET /step/{step_id}/{name}-autocomplete/search: Enables searching for specific plugins for a given step and name.

Dependencies:
- FastAPI for routing and dependency injection.
- SQLAlchemy for database session management.
- Latios for logging.

"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.schemas.plugin_schemas import PluginCreate,PluginWithIdDto
from ina_ground_control.models.plugin_model import Plugin
from ina_ground_control.services.plugin_service import get_plugins_search,create_plugin_crud,get_plugins_crud,delete_plugin_crud

logger = get_logger()
router = APIRouter(tags=["plugin"])
NOT_FOUND_STR = "Plugin not found"

#search plugins
@router.get("/step/{step_id}/{name}-autocomplete/search", response_model=list[PluginCreate])
def search_plugins(step_id: int, name: str, db: Session = Depends(get_db)):
    """
    Retrieve a list of plugins for a specific step and name.

    Args:
        step_id (int): The ID of the step for which plugins are to be retrieved.
        name (str): The name used for plugin autocomplete search.
        db (Session): The database session dependency.

    Returns:
        list[PluginCreate]: A list of plugins matching the specified criteria.

    Raises:
        HTTPException: If no plugins are found for the given parameters.
    """

    plugins = get_plugins_search(db, step_id=step_id, name=name)
    if plugins is None:
        logger.error("Failed to retrieve plugins")
        raise HTTPException(status_code=404, detail="plugins not found")
    return plugins

@router.get("/plugins/", response_model=list[PluginWithIdDto])
def read_plugins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[Plugin]:
    """Retrieve a list of plugins with pagination support."""
    plugins = get_plugins_crud(db, skip=skip, limit=limit)
    return plugins

#add new plugin
@router.post("/plugin/", response_model=PluginCreate)
def create_plugin(plugin: PluginCreate, db: Session = Depends(get_db)):
    """
    Create a new plugin.

    Args:
        plugin (PluginCreate): The plugin data to be created.

    Returns:
        PluginCreate: The newly created plugin's details.
    """
    try:
        return create_plugin_crud(plugin, db)
    except Exception as e:
        logger.error("Failed to create plugin: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create plugin") from e

@router.delete("/plugin/{plugin_id}", status_code=status.HTTP_200_OK,response_model=PluginWithIdDto)
def delete_plugin(plugin_id: int, db: Session = Depends(get_db)):
    """Delete a plugin by ID."""
    deleted_plugin = delete_plugin_crud(db, plugin_id)
    if deleted_plugin is None:
        logger.error("Failed to delete plugin with id: %d", plugin_id)
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR)
    return deleted_plugin
