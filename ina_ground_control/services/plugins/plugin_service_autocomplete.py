"""
This module provides search operation for plugin.

"""

import json
import logging

import requests
from jsonpath_ng.ext import parse as jsonpath_parse
from requests.exceptions import RequestException

from ina_ground_control import logger
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
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
                verify=True,
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
                data = self.parse(response)

                if not data:
                    logger.warning("Parsed response is empty for query: %s", query)

                return data

            else:
                logger.warning("Unexpected HTTP status code %d", response.status_code)
                response.raise_for_status()

        except RequestException as req_exc:
            logger.error("HTTP request failed: %s", str(req_exc))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Failed to fetch autocomplete results from the data source.",
            ) from req_exc

        except Exception as exc:
            logger.error("Unexpected error during autocomplete search: %s", str(exc))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Unexpected error occurred during autocomplete operation.",
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

    def _parse_json_response(self, response) -> dict | None:
        """
        Parse JSON response content.

        Args:
            response: The HTTP response object.

        Returns:
            dict | None: Parsed JSON data or None if parsing fails.
        """
        try:
            content = response.content.decode("utf-8-sig")
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON response: %s", e)
            return None

    def _extract_jsonpath_results(self, data: dict) -> dict:
        """
        Extract data using JSONPath expressions from configuration.

        Args:
            data (dict): The JSON data to extract from.

        Returns:
            dict: Dictionary containing extracted lists for each field.
        """
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

        return {
            "ids": id_expr.find(data),
            "ext_ids": ext_id_expr.find(data),
            "labels": label_expr.find(data),
            "images": image_expr.find(data) if image_expr else [],
            "descriptions": description_expr.find(data) if description_expr else [],
            "categories": categories_expr.find(data) if categories_expr else [],
        }

    def _transform_to_dto_list(
        self, extracted_data: dict
    ) -> list[PluginAutocompleteValueDTO]:
        """
        Transform extracted JSONPath results into DTO objects.

        Args:
            extracted_data (dict): Dictionary containing extracted data lists.

        Returns:
            list[PluginAutocompleteValueDTO]: List of transformed DTO objects.
        """
        ids = extracted_data["ids"]
        ext_ids = extracted_data["ext_ids"]
        labels = extracted_data["labels"]
        images = extracted_data["images"]
        descriptions = extracted_data["descriptions"]
        categories = extracted_data["categories"]

        num_results = len(ids)
        transformed_data = []

        for i in range(num_results):
            transformed_data.append(
                PluginAutocompleteValueDTO(
                    id=ids[i].value if i < len(ids) and ids[i] else None,
                    ext_id=(
                        ext_ids[i].value if i < len(ext_ids) and ext_ids[i] else None
                    ),
                    label=labels[i].value if i < len(labels) and labels[i] else None,
                    image=images[i].value if i < len(images) and images[i] else None,
                    description=(
                        descriptions[i].value
                        if i < len(descriptions) and descriptions[i]
                        else None
                    ),
                    categories=(
                        categories[i].value
                        if i < len(categories) and categories[i]
                        else None
                    ),
                )
            )

        return transformed_data

    def _should_filter_results(self, query: str, transformed_data: list) -> bool:
        """
        Determine if results should be filtered based on query.

        Args:
            query (str): The search query string.
            transformed_data (list): The transformed data list.

        Returns:
            bool: True if filtering should be applied, False otherwise.
        """
        if not query or not query.strip():
            return False
        if not self.config.search_query:
            return False
        if self.config.type == PluginConfigType.PLUGIN_REQUEST_POST:
            return False
        if not transformed_data:
            return False

        first_item_attr = getattr(transformed_data[0], self.config.search_query, None)
        return isinstance(first_item_attr, str)

    def _filter_and_sort_results(
        self, transformed_data: list[PluginAutocompleteValueDTO], query: str
    ) -> list[PluginAutocompleteValueDTO]:
        """
        Filter and sort results based on query position in search attribute.

        Args:
            transformed_data (list[PluginAutocompleteValueDTO]): The data to filter.
            query (str): The search query string.

        Returns:
            list[PluginAutocompleteValueDTO]: Filtered and sorted results.
        """

        def get_query_position(item):
            attr_value = getattr(item, self.config.search_query, "")
            if isinstance(attr_value, str):
                return attr_value.lower().find(query.lower())
            return -1

        filtered_data = [
            item for item in transformed_data if get_query_position(item) != -1
        ]
        return sorted(filtered_data, key=get_query_position)

    def _safe_extract_value(self, expr_results: list, index: int):
        """
        Safely extract value from JSONPath results.

        Args:
            expr_results (list): List of JSONPath match results.
            index (int): Index to extract from.

        Returns:
            The extracted value or None if not available.
        """
        if index < len(expr_results) and expr_results[index] is not None:
            try:
                return str(expr_results[index].value)
            except AttributeError:
                return expr_results[index]
        return None

    def _safe_jsonpath_parse(self, expression: str, field_name: str):
        """
        Safely parse JSONPath expression with better error handling.

        Args:
            expression (str): The JSONPath expression to parse.
            field_name (str): The field name for error messages.

        Returns:
            Parsed JSONPath expression or None if empty.

        Raises:
            GroundControlException: If expression is invalid.
        """
        if not expression:
            return None
        try:
            return jsonpath_parse(expression)
        except Exception as e:
            logger.error(
                "Invalid JSONPath expression for %s: %s - %s",
                field_name,
                expression,
                e,
            )
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details=f"Invalid JSONPath expression for {field_name}: {expression}",
            ) from e

    def _parse_jsonpath_expressions(self) -> dict:
        """
        Parse all JSONPath expressions from configuration.

        Returns:
            dict: Dictionary containing all parsed JSONPath expressions.

        Raises:
            GroundControlException: If required expressions are missing or invalid.
        """
        id_expr = self._safe_jsonpath_parse(
            self.config.response_id_key, "response_id_key"
        )
        ext_id_expr = self._safe_jsonpath_parse(
            self.config.response_ext_id_key, "response_ext_id_key"
        )
        label_expr = self._safe_jsonpath_parse(
            self.config.response_label_key, "response_label_key"
        )
        image_expr = self._safe_jsonpath_parse(
            self.config.response_image_key, "response_image_key"
        )
        description_expr = self._safe_jsonpath_parse(
            self.config.response_description_key, "response_description_key"
        )
        categories_expr = self._safe_jsonpath_parse(
            self.config.response_categories_key, "response_categories_key"
        )

        if not id_expr:
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Missing required JSONPath expression for response_id_key",
            )

        return {
            "id_expr": id_expr,
            "ext_id_expr": ext_id_expr,
            "label_expr": label_expr,
            "image_expr": image_expr,
            "description_expr": description_expr,
            "categories_expr": categories_expr,
        }

    def _extract_jsonpath_data(self, data: dict, expressions: dict) -> dict:
        """
        Extract data using JSONPath expressions.

        Args:
            data (dict): The JSON data to extract from.
            expressions (dict): Dictionary of parsed JSONPath expressions.

        Returns:
            dict: Dictionary containing extracted lists for each field.
        """
        return {
            "ids": expressions["id_expr"].find(data) if expressions["id_expr"] else [],
            "ext_ids": (
                expressions["ext_id_expr"].find(data)
                if expressions["ext_id_expr"]
                else []
            ),
            "labels": (
                expressions["label_expr"].find(data)
                if expressions["label_expr"]
                else []
            ),
            "images": (
                expressions["image_expr"].find(data)
                if expressions["image_expr"]
                else []
            ),
            "descriptions": (
                expressions["description_expr"].find(data)
                if expressions["description_expr"]
                else []
            ),
            "categories": (
                expressions["categories_expr"].find(data)
                if expressions["categories_expr"]
                else []
            ),
        }

    def _create_dto_from_extracted_data(
        self, extracted_data: dict, index: int
    ) -> PluginAutocompleteValueDTO:
        """
        Create a DTO object from extracted data at given index.

        Args:
            extracted_data (dict): Dictionary containing extracted data lists.
            index (int): Index to create DTO from.

        Returns:
            PluginAutocompleteValueDTO: The created DTO object.
        """
        return PluginAutocompleteValueDTO(
            id=self._safe_extract_value(extracted_data["ids"], index),
            ext_id=self._safe_extract_value(extracted_data["ext_ids"], index),
            label=self._safe_extract_value(extracted_data["labels"], index),
            image=self._safe_extract_value(extracted_data["images"], index),
            description=self._safe_extract_value(extracted_data["descriptions"], index),
            categories=self._safe_extract_value(extracted_data["categories"], index),
        )

    def _build_transformed_data(
        self, extracted_data: dict
    ) -> list[PluginAutocompleteValueDTO]:
        """
        Build list of DTOs from extracted data.

        Args:
            extracted_data (dict): Dictionary containing extracted data lists.

        Returns:
            list[PluginAutocompleteValueDTO]: List of transformed DTO objects.
        """
        num_results = len(extracted_data["ids"])
        logger.debug("Found %d results to process", num_results)

        transformed_data = []
        for i in range(num_results):
            try:
                item_data = self._create_dto_from_extracted_data(extracted_data, i)
                transformed_data.append(item_data)
            except Exception as e:
                logger.warning("Failed to process item %d: %s", i, e)
                continue

        return transformed_data

    def _apply_filtering_if_needed(
        self, transformed_data: list[PluginAutocompleteValueDTO], query: str
    ) -> list[PluginAutocompleteValueDTO]:
        """
        Apply filtering and sorting to transformed data if conditions are met.

        Args:
            transformed_data (list[PluginAutocompleteValueDTO]): The data to filter.
            query (str): The search query string.

        Returns:
            list[PluginAutocompleteValueDTO]: Filtered results or original data.
        """
        if not self._should_filter_results(query, transformed_data):
            return transformed_data

        try:
            return self._filter_and_sort_results(transformed_data, query)
        except Exception as e:
            logger.warning(
                "Error during result filtering, returning unfiltered results: %s", e
            )
            return transformed_data

    def parse(self, response) -> list[PluginAutocompleteValueDTO]:
        """
        Parses the HTTP response into a list of `PluginAutocompleteValueDTO` objects.

        Args:
            response: The HTTP response object.

        Returns:
            list[PluginAutocompleteValueDTO]: A list of transformed autocomplete value objects.

        Raises:
            GroundControlException: If parsing fails or data is invalid.
        """
        if self.config.data_type != DataTypeEnum.JSON:
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details=f"Unsupported data type: {self.config.data_type}",
            )

        data = self._parse_json_response(response)
        if data is None:
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Invalid JSON response",
            )

        if not data:
            logger.warning("JSON response is empty.")
            return []

        try:
            expressions = self._parse_jsonpath_expressions()
            extracted_data = self._extract_jsonpath_data(data, expressions)

            if not extracted_data["ids"]:
                logger.warning(
                    "No ID fields found in response using JSONPath: %s",
                    self.config.response_id_key,
                )
                return []

            return self._build_transformed_data(extracted_data)

        except GroundControlException:
            raise
        except Exception as e:
            logger.error("Error processing JSON response: %s", e)
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details=f"Failed to process response data: {str(e)}",
            ) from e
