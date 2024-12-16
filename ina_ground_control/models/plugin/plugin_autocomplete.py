"""
This module defines the configuration for plugin autocomplete functionality.
"""

from typing import Optional
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase


class PluginConfigAutoComplete(PluginConfigBase):
    """
       Configuration for plugin autocomplete functionality.

       Attributes:
           search_attr (str): Attribute to search by (e.g., title or description).
           search_query_param (str): Query parameter used in the search request. Default is 'q'.
           search_item_size (int): Maximum number of items to return. Default is 30.
           search_item_sort (str): Sorting criteria for items. Default is 'title,sc'.
       """
    search_attr: Optional[str]
    search_query_param: Optional[str]
    search_item_size: Optional[int]
    search_item_sort: Optional[str]