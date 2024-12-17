import logging

import requests
from requests.exceptions import RequestException

from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.PluginAutocompleteValueDTO import PluginAutocompleteValueDTO
from ina_ground_control.services.plugins.plugin_service_base import PluginServiceBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginServiceAutoComplete(PluginServiceBase):
    def __init__(self, config: PluginConfigAutoComplete):
        self.config = config

    def search(self, query: str) -> list[PluginAutocompleteValueDTO]:
        """
        Perform an autocomplete search using the configured data source and query parameter.

        Args:
            query (str): The search query string.

        Returns:
            list[PluginAutocompleteValueDTO]: A list of matched PluginAutocompleteValueDTO objects.

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
        pass

    def parse(self, response) -> list[PluginAutocompleteValueDTO]:
        if self.config.data_type == "json":
            data = response.json()
            transformed_data = [
                # TODO change config id and use jsonpath
                PluginAutocompleteValueDTO(
                    id=item.get("id"),
                    extId=item.get("code"),  # Mapping "code" to "extId"
                    label=item.get("label")
                )
                for item in data
            ]
            return transformed_data
        else:
            raise Exception(f"Unknown data type: {self.config.data_type} ")
