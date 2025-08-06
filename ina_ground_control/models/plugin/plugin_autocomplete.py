"""
This module defines the configuration for plugin autocomplete functionality.
"""

from typing import Optional, Union

from pydantic import ConfigDict

from ina_ground_control.models.plugin.plugin_base import PluginConfigBase


class PluginConfigAutoComplete(PluginConfigBase):
    """
    Configuration for plugin autocomplete functionality.

    Attributes:
        search_query (Union[str, dict]):
            The search query used to perform autocomplete.
            - Can be a simple string for GET-based plugins (e.g., simple search like with json file).
            - Or a full JSON object (dict) for POST-based plugins (e.g., ElasticSearch).
        response_id_key (str): JSONPath to extract the result ID from the response.
        response_ext_id_key (str): JSONPath to extract the external ID from the response.
        response_label_key (str): JSONPath to extract the label from the response.
        response_image_key (str): JSONPath to extract the image URL.
        response_description_key (str): JSONPath to extract a textual description.
    """
    search_query: Optional[Union[str, dict]] = None
    response_id_key: Optional[str] = None
    response_ext_id_key: Optional[str] = None
    response_label_key: Optional[str] = None
    response_image_key: Optional[str] = None
    response_description_key: Optional[str] = None

    # Use ConfigDict for configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra='allow'
    )
