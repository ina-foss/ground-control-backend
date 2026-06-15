"""
This module provides search operation for plugin.

"""

import json
import logging

import requests
from jsonpath_ng.ext import parse as jsonpath_parse
from requests.exceptions import HTTPError, RequestException
from requests_oauth2client import OAuth2Client

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
from ina_ground_control.utils.crypto import get_secret_cipher

logger = logging.getLogger(__name__)
PLUGIN_GLOBAL_TIMEOUT = 10


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

    config: PluginConfigAutoComplete

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
        if not self.config.data_source:
            return None
        try:
            details = requests.get(
                self.config.data_source,
                params=params,
                timeout=PLUGIN_GLOBAL_TIMEOUT,
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

    def _get_access_token(self) -> str | None:
        """
        Fetch an OAuth2 access token using client credentials if auth config is present.

        Returns:
            str | None: The access token string, or None if no auth config is set.

        Raises:
            GroundControlException: If the token request fails.
        """
        if not (
            self.config.token_url
            and self.config.client_id
            and self.config.client_secret
        ):
            return None
        try:
            logger.info(
                "Requesting token — url=%s client_id=%s",
                self.config.token_url,
                self.config.client_id,
            )
            oauth2client = OAuth2Client(
                token_endpoint=self.config.token_url,
                client_id=self.config.client_id,
                client_secret=get_secret_cipher().decrypt(self.config.client_secret),
            )
            token_response = oauth2client.client_credentials()
            return token_response.access_token
        except Exception as e:
            logger.error("Failed to fetch access token: %s", str(e))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Failed to obtain access token from the token endpoint.",
            ) from e

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
            if not self.config.data_source:
                raise GroundControlException(
                    ErrorCode.GENERIC_CLIENT_ERROR,
                    details="Plugin configuration is missing 'data_source'.",
                )
            no_verify = True
            headers = {"Content-Type": "application/json"}

            access_token = self._get_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
                logger.info(
                    "Access token obtained — Authorization header: Bearer %s...",
                    str(access_token)[:20],
                )
            else:
                logger.warning(
                    "No auth config found for plugin (token_url=%s, client_id=%s) — "
                    "request will be sent without Authorization header.",
                    self.config.token_url,
                    self.config.client_id,
                )

            # Handle PLUGIN_REQUEST_POST (e.g., Elasticsearch)
            if self.config.type == PluginConfigType.PLUGIN_REQUEST_POST:
                try:
                    query_json_str = json.dumps(self.config.search_query)
                    payload_str = query_json_str.replace("##query##", query)
                    payload = json.loads(payload_str)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON query string: %s", e)
                    raise ValueError("Query must be a valid JSON string.") from e

                logger.info(
                    "Sending POST request to data source: %s", self.config.data_source
                )
                response = requests.post(
                    self.config.data_source,
                    json=payload,
                    headers=headers,
                    timeout=PLUGIN_GLOBAL_TIMEOUT,
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

                logger.info(
                    "Sending GET request to data source type: %s",
                    self.config.data_source,
                )
                response = requests.get(
                    data_source,
                    headers=headers,
                    timeout=PLUGIN_GLOBAL_TIMEOUT,
                    verify=no_verify,
                )
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
                logger.info(
                    "Searching Wikidata entities for query: %s", query
                )  # NOSONAR
                response = requests.get(
                    self.config.data_source,
                    params=params,
                    timeout=PLUGIN_GLOBAL_TIMEOUT,
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
                            link=item.get("url"),
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
                    logger.warning(
                        "Parsed response is empty for query: %s", query
                    )  # NOSONAR

                return data

            else:
                logger.warning(
                    "Unexpected HTTP status code %d — response body: %s",
                    response.status_code,
                    response.text[:500],
                )
                response.raise_for_status()
                return []

        except HTTPError as http_exc:
            status_code = http_exc.response.status_code
            logger.error("HTTP request failed: %s", str(http_exc))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details=f"Data source returned HTTP {status_code}.",
            ) from http_exc

        except RequestException as req_exc:
            logger.error("HTTP request failed: %s", str(req_exc))
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Failed to connect to the data source.",
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

        if not isinstance(self.config.search_query, str):
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

    def _safe_jsonpath_parse(self, expression: str | None, field_name: str):
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
        tag_label_expr = self._safe_jsonpath_parse(
            self.config.response_tag_label_key, "response_tag_label_key"
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
        group_expr = self._safe_jsonpath_parse(
            self.config.response_group_key, "response_group_key"
        )
        editable_expr = self._safe_jsonpath_parse(
            self.config.response_editable_key, "response_editable_key"
        )
        copyable_expr = self._safe_jsonpath_parse(
            self.config.response_copyable_key, "response_copyable_key"
        )
        tooltip_expr = self._safe_jsonpath_parse(
            self.config.response_tooltip_key, "response_tooltip_key"
        )
        link_expr = self._safe_jsonpath_parse(
            self.config.response_link_key, "response_link_key"
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
            "tag_label_expr": tag_label_expr,
            "image_expr": image_expr,
            "description_expr": description_expr,
            "categories_expr": categories_expr,
            "group_expr": group_expr,
            "editable_expr": editable_expr,
            "copyable_expr": copyable_expr,
            "tooltip_expr": tooltip_expr,
            "link_expr": link_expr,
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
            "tag_labels": (
                expressions["tag_label_expr"].find(data)
                if expressions["tag_label_expr"]
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
            "group": (
                expressions["group_expr"].find(data)
                if expressions["group_expr"]
                else []
            ),
            "editable": (
                expressions["editable_expr"].find(data)
                if expressions["editable_expr"]
                else []
            ),
            "copyable": (
                expressions["copyable_expr"].find(data)
                if expressions["copyable_expr"]
                else []
            ),
            "tooltip": (
                expressions["tooltip_expr"].find(data)
                if expressions["tooltip_expr"]
                else []
            ),
            "link": (
                expressions["link_expr"].find(data) if expressions["link_expr"] else []
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
            tag_label=self._safe_extract_value(extracted_data["tag_labels"], index),
            image=self._safe_extract_value(extracted_data["images"], index),
            description=self._safe_extract_value(extracted_data["descriptions"], index),
            categories=self._safe_extract_value(extracted_data["categories"], index),
            group=self._safe_extract_value(extracted_data["group"], index),
            editable=self._safe_extract_value(extracted_data["editable"], index),
            copyable=self._safe_extract_value(extracted_data["copyable"], index),
            tooltip=self._safe_extract_value(extracted_data["tooltip"], index),
            link=self._safe_extract_value(extracted_data["link"], index),
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
