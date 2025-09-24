"""
This module provides search operation for plugin.

"""

import json
import logging

import requests
from jsonpath_ng.ext import parse as jsonpath_parse
from requests.exceptions import RequestException

from ina_ground_control import logger
from ina_ground_control.models.plugin.plugin_autocomplete import (
    PluginConfigAutoComplete,
)
from ina_ground_control.models.plugin.plugin_autocomplete_value_dto import (
    PluginAutocompleteValueDTO,
)
from ina_ground_control.models.plugin.plugin_base import DataTypeEnum, PluginConfigType
from ina_ground_control.services.plugins.plugin_service_base import PluginServiceBase

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

    def commons_url(self, filename: str) -> str:
        """
        Build the direct Wikimedia Commons URL for a given filename.

        Args:
            filename (str): The name of the file stored on Wikimedia Commons.

        Returns:
            str: The full URL pointing to the file on Wikimedia Commons.
        """
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"

    def get_wikidata_image(self, entity_id: str) -> str | None:
        """
        Retrieve the image URL associated with a Wikidata entity (if available).

        This method queries the Wikidata API for the entity's claims and
        extracts the image filename (property `P18`), then converts it into
        a direct Wikimedia Commons URL.

        Args:
            entity_id (str): The unique Wikidata entity identifier (e.g., "Q42").

        Returns:
            str | None: The direct Wikimedia Commons image URL if found,
            otherwise None.

        Raises:
            RequestException: If the HTTP request to the Wikidata API fails.
            ValueError: If the response cannot be decoded as JSON.
            KeyError: If the expected fields are missing in the API response.
        """
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "claims",
            "format": "json",
        }
        try:
            details = requests.get(
                self.config.data_source,
                params=params,
                timeout=30,
                verify=False,
                headers={"User-Agent": ""},
            ).json()
            claims = details.get("entities", {}).get(entity_id, {}).get("claims", {})
            if "P18" in claims:
                filename = claims["P18"][0]["mainsnak"]["datavalue"]["value"]
                return self.commons_url(filename)
        except (RequestException, ValueError, KeyError) as e:
            logger.warning("Failed to fetch image for entity %s: %s", entity_id, e)
        return None

    def search(self, query: str) -> list[PluginAutocompleteValueDTO]:
        """
        Perform an autocomplete search using the plugin configuration.

        For `PLUGIN_REQUEST_POST`, sends a POST request with the query parsed as JSON payload
        (e.g., for Elasticsearch).
        For `PLUGIN_REQUEST_GET`, sends a GET request with the query string as a parameter.

        Args:
            query (str): The search query string (raw or JSON depending on plugin type).

        Returns:
            list[PluginAutocompleteValueDTO]: A list of matched autocomplete values.

        Raises:
            ValueError: If query is expected to be JSON but is not valid JSON.
            RuntimeError: For unexpected errors or failed HTTP requests.
        """
        try:
            no_verify = False
            headers = {"Content-Type": "application/json"}

            # Handle PLUGIN_REQUEST_POST (e.g., Elasticsearch)
            if self.config.type == PluginConfigType.PLUGIN_REQUEST_POST:
                try:
                    query_json_str = json.dumps(self.config.search_query)
                    payload_str = query_json_str.replace("##query##", query)
                    payload = json.loads(payload_str)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON query string: %s", query)
                    raise ValueError("Query must be a valid JSON string.") from e

                logger.info(
                    "Sending POST request to data source: %s", self.config.data_source
                )
                response = requests.post(
                    self.config.data_source,
                    json=payload,
                    headers=headers,
                    timeout=30,
                    verify=no_verify,
                )
            # Handle PLUGIN_STATIC_DATA (simple json file)
            elif self.config.type == PluginConfigType.PLUGIN_STATIC_DATA:
                fake_response = requests.Response()
                fake_response.status_code = 200
                fake_response._content = (  # pylint: disable=protected-access
                    self.config.data_source.encode("utf-8")
                )
                response = fake_response
            # Handle PLUGIN_REQUEST_GET (simple RESTful API)
            elif self.config.type == PluginConfigType.PLUGIN_REQUEST_GET:
                if self.config.search_query:
                    data_source = (
                        f"{self.config.data_source}?{self.config.search_query}={query}"
                    )
                else:
                    data_source = self.config.data_source

                logger.info("Sending GET request to data source: %s", data_source)
                response = requests.get(data_source, timeout=30, verify=no_verify)
            # Handle PLUGIN_WIKIDATA
            elif self.config.type == PluginConfigType.PLUGIN_WIKIDATA:
                params = {
                    "action": "wbsearchentities",
                    "format": "json",
                    "language": "fr",
                    "uselang": "fr",
                    "type": "item",
                    "search": query,
                }
                logger.info("Searching Wikidata entities for query: %s", query)
                response = requests.get(
                    self.config.data_source,
                    params=params,
                    timeout=30,
                    verify=no_verify,
                    headers={"User-Agent": ""},
                )
                data = response.json()
                results: list[PluginAutocompleteValueDTO] = []
                for item in data.get("search", []):
                    entity_id = item["id"]
                    image_url = self.get_wikidata_image(entity_id)

                    results.append(
                        PluginAutocompleteValueDTO(
                            id=entity_id,
                            ext_id=entity_id,
                            label=item.get("label"),
                            description=item.get("description"),
                            image=image_url,
                        )
                    )

                return results
            else:
                logger.error("Unsupported plugin type: %s", self.config.type)
                raise ValueError(f"Unsupported plugin type: {self.config.type}")

            # Handle response
            if response.status_code == 200:
                logger.info("Received successful response from data source.")
                data = self.parse(
                    response,
                    (
                        query
                        if self.config.type == PluginConfigType.PLUGIN_REQUEST_GET
                        else None
                    ),
                )

                if not data:
                    logger.warning("Parsed response is empty for query: %s", query)

                return data

            else:
                logger.warning("Unexpected HTTP status code %d", response.status_code)
                response.raise_for_status()

        except RequestException as req_exc:
            logger.error("HTTP request failed: %s", str(req_exc))
            raise RuntimeError(
                "Failed to fetch autocomplete results from the data source."
            ) from req_exc

        except Exception as exc:
            logger.error("Unexpected error during autocomplete search: %s", str(exc))
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

    def parse(self, response, query) -> list[PluginAutocompleteValueDTO]:
        """
        Parses the HTTP response into a list of `PluginAutocompleteValueDTO` objects.

        Args:
            response: The HTTP response object.
            query: search string

        Returns:
            list[PluginAutocompleteValueDTO]: A list of transformed autocomplete value objects.

        Raises:
            Exception: If the response's data type is unknown.
        """
        if self.config.data_type == DataTypeEnum.JSON:
            try:
                # Handle potential UTF-8 BOM in the response
                content = response.content.decode("utf-8-sig")
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON response: %s", e)
            if data:
                id_expr = jsonpath_parse(self.config.response_id_key)
                ext_id_expr = jsonpath_parse(self.config.response_ext_id_key)
                label_expr = jsonpath_parse(self.config.response_label_key)
                image_expr = (
                    jsonpath_parse(self.config.response_image_key)
                    if self.config.response_image_key
                    else None
                )
                description_expr = (
                    jsonpath_parse(self.config.response_description_key)
                    if self.config.response_description_key
                    else None
                )
                categories_expr = (
                    jsonpath_parse(self.config.response_categories_key)
                    if self.config.response_categories_key
                    else None
                )

                ids = id_expr.find(data)
                ext_ids = ext_id_expr.find(data)
                labels = label_expr.find(data)
                images = image_expr.find(data) if image_expr else [None] * len(ids)
                descriptions = (
                    description_expr.find(data)
                    if description_expr
                    else [None] * len(ids)
                )
                categories = (
                    categories_expr.find(data) if categories_expr else [None] * len(ids)
                )

                transformed_data = [
                    PluginAutocompleteValueDTO(
                        id=id_match.value if id_match else None,
                        ext_id=ext_id_match.value if ext_id_match else None,
                        label=label_match.value if label_match else None,
                        image=image_match.value if image_match else None,
                        description=(
                            description_match.value if description_match else None
                        ),
                        categories=(
                            categories_match.value if categories_match else None
                        ),
                    )
                    for id_match, ext_id_match, label_match, image_match, description_match, categories_match in zip(
                        ids, ext_ids, labels, images, descriptions, categories
                    )
                ]
                # filter only if the search attribute is defined and a string, else return the unfiltered array
                if (
                    query
                    and query.strip()
                    and self.config.search_query
                    and self.config.type != PluginConfigType.POST_PLUGIN
                    and isinstance(
                        getattr(transformed_data[0], self.config.search_query), str
                    )
                ):

                    def get_query_position(item):
                        attr_value = getattr(item, self.config.search_query, "")
                        if isinstance(attr_value, str):
                            return attr_value.lower().find(query.lower())
                        return -1

                    filtred_transformed_data = [
                        item
                        for item in transformed_data
                        if get_query_position(item) != -1
                    ]
                    transformed_data = sorted(
                        filtred_transformed_data, key=get_query_position
                    )
                return transformed_data
            else:
                logger.warning("JSON response is empty.")
                return []
        else:
            raise ValueError(f"Unknown data type: {self.config.data_type} ")
