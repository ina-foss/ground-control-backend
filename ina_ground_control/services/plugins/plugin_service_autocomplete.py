"""
This module provides search operation for plugin.

"""
import logging
import requests
from requests.exceptions import RequestException
from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_autocomplete_value_dto import PluginAutocompleteValueDTO
from ina_ground_control.services.plugins.plugin_service_base import PluginServiceBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginServiceAutoComplete(PluginServiceBase):
    """
    Service for handling autocomplete functionality in a plugin.

    This class extends `PluginServiceBase` to implement functionality for
    querying and processing autocomplete data based on a configurable data source.

    Attributes:
        config (PluginConfigAutoComplete): Configuration object specifying
            the data source and parameters for the autocomplete service.

    Methods:
        search(query: str) -> list[PluginAutocompleteValueDTO]:
            Executes an autocomplete search using the provided query and returns a
            list of matching autocomplete values.

        add(data: dict):
            Placeholder for adding data (not yet implemented).

        parse(response) -> list[PluginAutocompleteValueDTO]:
            Parses the HTTP response into a list of `PluginAutocompleteValueDTO` objects.
    """
    def __init__(self, config: PluginConfigAutoComplete):
        """
        Initializes the PluginServiceAutoComplete with the provided configuration.

        Args:
            config (PluginConfigAutoComplete): The configuration object
                specifying the data source and related settings.
        """
        super().__init__(config)
        self.config = config

    def search(self, query: str) -> list[PluginAutocompleteValueDTO]:
        """
        Perform an autocomplete search using the configured data source and query parameter.

        Args:
            query (str): The search query string.

        Returns:
            list[PluginAutocompleteValueDTO]: A list of matched `PluginAutocompleteValueDTO` objects.

        Raises:
            RuntimeError: If the HTTP request or response parsing fails.
        """
        try:
            # Construct the data source URL
            if self.config.search_query_param:
                data_source = f"{self.config.data_source}?{self.config.search_query_param}={query}"
            else:
                data_source = self.config.data_source

            logger.info("Sending request to data source: %s", data_source)

            # Make an HTTP GET request
            response = requests.get(data_source, timeout=30)

            # Check if the HTTP response status is OK
            if response.status_code == 200:
                logger.info("Received successful response from data source.")
                data = self.parse(response)

                if not data:
                    logger.warning("Parsed response is empty for query: %s", query)

                return data
            else:
                # Log warning for non-200 responses
                logger.warning(
                    "Unexpected HTTP response status code %d received from data source.",
                    response.status_code,
                )
                response.raise_for_status()

        except RequestException as req_exc:
            logger.error(
                "HTTP request to data source failed with error: %s", str(req_exc)
            )
            raise RuntimeError(
                "Failed to fetch autocomplete results from the data source."
            ) from req_exc

        except Exception as exc:
            logger.error(
                "An unexpected error occurred while performing the search: %s",
                str(exc),
            )
            raise RuntimeError(
                "Unexpected error occurred during autocomplete operation."
            ) from exc

    def add(self, data: dict):
        """
       Placeholder for adding data to the autocomplete service.

       Args:
           data (dict): The data to be added.

       Note:
           This method is not implemented in the current version.
       """
        pass

    def parse(self, response) -> list[PluginAutocompleteValueDTO]:
        """
       Parses the HTTP response into a list of `PluginAutocompleteValueDTO` objects.

       Args:
           response: The HTTP response object.

       Returns:
           list[PluginAutocompleteValueDTO]: A list of transformed autocomplete value objects.

       Raises:
           Exception: If the response's data type is unknown.
       """
        if self.config.data_type == "json":
            data = response.json()
            transformed_data = [
                # TODO change config id and use jsonpath
                PluginAutocompleteValueDTO(
                    id=item.get("id"),
                    ext_id=item.get("code"),  # Mapping "code" to "extId"
                    label=item.get("label")
                )
                for item in data
            ]
            return transformed_data
        else:
            raise ValueError(f"Unknown data type: {self.config.data_type} ")
