"""
This module provides CRUD operations for plugins.

It includes functions to retrieve a plugins by ID_step and name.
"""

from requests_oauth2client import OAuth2Client
from sqlalchemy.orm import Session

from ina_ground_control import logger
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.plugin.plugin_autocomplete import (
    PluginConfigAutoComplete,
)
from ina_ground_control.models.plugin.plugin_config import PluginConfigDTO
from ina_ground_control.models.plugin_model import DisplayZone, Plugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate
from ina_ground_control.services.plugins.plugin_service_autocomplete import (
    PluginServiceAutoComplete,
)


def request_auth_token(
    token_url: str, client_id: str, client_secret: str
) -> OAuth2Client:
    try:
        oauth2client = OAuth2Client(
            token_endpoint=token_url,
            client_id=client_id,
            client_secret=client_secret,
            testing=True,
        )
        token_response = oauth2client.fetch_token()
        return token_response.access_token
    except Exception as e:
        logger.error("Error requesting Keycloak token via OAuth2Client: %s", str(e))
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR,
            details="Failed to obtain access token from Keycloak",
        ) from e


def create_plugin_crud(plugin: PluginCreate, db: Session):
    """
    Create a new plugin in the database.

    Attributes:
        plugin (PluginCreate): The step data transfer object containing plugin details.
        db (Session): The database session used for querying.

    Returns:
        Plugin: The newly created Plugin object.
    """
    config = plugin.config_data

    if config.token_url and config.client_id and config.client_secret:
        request_auth_token(config.token_url, config.client_id, config.client_secret)
        try:
            logger.info(
                "Successfully connected to protected resource: %s", config.data_source
            )
            # TODO add how get data source
        except Exception as e:
            logger.error("Failed to access protected resource: %s", str(e))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details=f"Unable to access {config.data_source} with obtained token",
            ) from e

    plugin_data = plugin.model_dump()
    children_data = plugin_data.pop("children", [])
    children_models = [Plugin(**child) for child in children_data]
    db_plugin = Plugin(**plugin_data)
    db_plugin.children = children_models
    db.add(db_plugin)
    db.commit()
    db.refresh(db_plugin)
    return db_plugin


def get_plugins_search(db: Session, plugin_id: int, query: str):
    plugin = get_plugin_by_id(db, plugin_id)
    config = PluginConfigDTO.build(plugin.config_data)
    if isinstance(config, PluginConfigAutoComplete):
        plugin = PluginServiceAutoComplete(config)
        return plugin.search(query)
    else:
        raise NotImplementedError(f"{str(config)} not implemented")


def get_plugins_crud(
    db: Session,
    step_id: int,
    zone: str | list[DisplayZone],
    plugin_type: str | None = None,
):
    query = db.query(Plugin).filter(
        Plugin.step_id == step_id,
    )
    if isinstance(zone, str):
        query = query.filter(Plugin.display_zone == zone)
    elif isinstance(zone, list):
        query = query.filter(Plugin.display_zone.in_(zone))
    if plugin_type:
        query = query.filter(Plugin.type == plugin_type)
        query = query.order_by(Plugin.display_config["order"].as_integer().asc())
    return query.all()


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
