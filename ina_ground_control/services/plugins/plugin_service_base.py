"""
This module provides search and add operations for PluginServiceBase.

"""
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase


class PluginServiceBase:
    """
    Base class for implementing plugin services.

    This class serves as a foundation for creating custom plugin services
    with specific configurations. It provides a template for adding and
    searching data in the context of a plugin.

    Attributes:
        config (PluginConfigBase): The configuration object for the plugin service.

    Methods:
        search(value: str):
            Searches for a specific value. This method should be implemented
            by subclasses with the desired search logic.

        add(data: dict):
            Adds new data to the plugin. This method should be implemented
            by subclasses to handle data insertion logic.
    """

    def __init__(self, config: PluginConfigBase):
        """
       Initializes the PluginServiceBase with the provided configuration.

       Args:
           config (PluginConfigBase): The configuration object for the plugin service.
       """
        self.config = config

    def search(self, query: str):
        """
       Searches for a specific value.

       Args:
           value (str): The value to search for.

       Raises:
           NotImplementedError: This method is intended to be overridden by subclasses.
       """
        pass

    def add(self, data: dict):
        """
       Adds new data to the plugin.

       Args:
           data (dict): The data to be added.

       Raises:
           NotImplementedError: This method is intended to be overridden by subclasses.
       """
        pass
