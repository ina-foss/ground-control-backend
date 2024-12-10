from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.models.plugin_model import Plugin
from ina_ground_control.schemas.plugin_schemas import PluginCreate
from ina_ground_control.services.plugin_service import get_plugins

logger = get_logger()
router = APIRouter(tags=["plugin"])

#search plugins
@router.get("/step/{step_id}/{name}-autocomplete/search", response_model=list[PluginCreate])
def getPlugins(step_id: int,name:str, db: Session = Depends(get_db)):
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

    plugins = get_plugins(db, step_id=step_id,name=name)
    if plugins is None:
        logger.error("Failed to retrieve plugins")
        raise HTTPException(status_code=404, detail="plugins not found")
    return plugins
