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

"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_keycloak_middleware import (
    AuthorizationResult,
    CheckPermissions,
    MatchStrategy,
)
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.plugin.plugin_autocomplete_value_dto import (
    PluginAutocompleteValueDTO,
)
from ina_ground_control.models.plugin_model import DisplayZone, Plugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate, PluginWithIdDto
from ina_ground_control.services.plugin_service import (
    create_plugin_crud,
    delete_plugin_crud,
    get_plugin_by_id,
    get_plugins_crud,
    get_plugins_search,
    update_plugin_crud,
)

router = APIRouter(tags=["plugin"])


# search plugins
@router.get(
    "/plugins/{plugin_id}/search", response_model=list[PluginAutocompleteValueDTO]
)
def search_plugins(plugin_id: int, query: str, db: Session = Depends(get_db)):
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

    plugins = get_plugins_search(db, plugin_id=plugin_id, query=query)
    if plugins is None:
        logger.error("Failed to retrieve plugins")
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Plugin", id=plugin_id
        )
    return plugins


@router.get(
    "/plugins/step/{step_id}/{plugin_type}/display/{zone}",
    response_model=list[PluginWithIdDto],
)
def read_plugins(
    db: Session = Depends(get_db), step_id=int, plugin_type=str, zone=str
) -> list[Plugin]:
    """Retrieve a list of plugins with pagination support."""
    plugins = get_plugins_crud(db, step_id=step_id, plugin_type=plugin_type, zone=zone)
    return plugins


@router.get("/plugins/step/{step_id}/display/", response_model=list[PluginWithIdDto])
def read_all_plugins(
    step_id: int,
    zone: Annotated[list[DisplayZone], Query()],
    db: Session = Depends(get_db),
) -> list[Plugin]:
    """
    Retrieve plugins for a given step and display zone,
    only those with display_config set, ordered by display_config['order'].
    """
    plugins = get_plugins_crud(db, step_id=step_id, zone=zone)
    return plugins


# add new plugin
@router.post("/plugin", response_model=PluginWithIdDto)
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
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Failed to create plugin"
        ) from e


# update an existing plugin
@router.patch(
    "/plugin/{plugin_id}",
    status_code=status.HTTP_200_OK,
    response_model=PluginWithIdDto,
)
def update_plugin(
    plugin_id: int,
    plugin: PluginCreate,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.UPDATE_PLUGIN.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
):
    """Update an existing plugin by ID."""
    updated_plugin = update_plugin_crud(plugin_id, plugin, db)
    if updated_plugin is None:
        logger.error("Failed to update plugin with id: %d", plugin_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Plugin", id=plugin_id
        )
    return updated_plugin


@router.delete(
    "/plugin/{plugin_id}",
    status_code=status.HTTP_200_OK,
    response_model=PluginWithIdDto,
)
def delete_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    _authorization_result: AuthorizationResult = Depends(
        CheckPermissions(
            [Permission.DELETE_PLUGIN.value], match_strategy=MatchStrategy.AND
        )
    ),
    # pylint: disable=invalid-name
):
    """Delete a plugin by ID."""
    deleted_plugin = delete_plugin_crud(db, plugin_id)
    if deleted_plugin is None:
        logger.error("Failed to delete plugin with id: %d", plugin_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Plugin", id=plugin_id
        )
    return deleted_plugin


@router.get(
    "/plugin/{plugin_id}", response_model=PluginWithIdDto, response_model_by_alias=False
)
def read_plugin(plugin_id: int, db: Session = Depends(get_db)) -> Plugin:
    """Get details of a single plugin by ID."""
    plugin = get_plugin_by_id(db, plugin_id=plugin_id)
    if plugin is None:
        logger.error("Failed to retrieve plugin with id: %d", plugin_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Plugin", id=plugin_id
        )
    return plugin
