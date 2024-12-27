import unittest
from unittest.mock import Mock, patch
from requests.models import Response
from requests.exceptions import RequestException
from ina_ground_control.services.plugins.plugin_service_autocomplete import PluginServiceAutoComplete
from ina_ground_control.models.plugin.plugin_autocomplete_value_dto import PluginAutocompleteValueDTO
from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
import json

"""{"type": "plugin_autocomplete",
 "data_source": '"https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json"',
 "data_type": "json",
 "search_attr": "",
 "search_query_param": "q",
 "search_item_sort": "title,asc",
 "response_id_key": "id",
 "response_ext_id_key": "ext_id",
 "response_label_key": "label",
 }"""
class TestPluginServiceAutoComplete(unittest.TestCase):

    def setUp(self):
        self.config = PluginConfigAutoComplete(
            data_source="https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
            search_attr="query",
            data_type="json",
            type="plugin_autocomplete",
            response_id_key= "id",
            response_ext_id_key= "ext_id",
            response_label_key= "label",
        )
        self.service = PluginServiceAutoComplete(config=self.config)

    @patch("ina_ground_control.services.plugins.plugin_service_autocomplete.requests.get")
    def test_search_valid_response(self, mock_get):
        """Test the `search` method with a valid HTTP response."""
        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.content = json.dumps([
            {"id": "1", "code": "A123", "label": "Item 1"},
            {"id": "2", "code": "B456", "label": "Item 2"}
        ]).encode("utf-8")
        mock_get.return_value = mock_response

        # Expected result
        expected_result = [
            PluginAutocompleteValueDTO(id="1", ext_id="A123", label="Item 1"),
            PluginAutocompleteValueDTO(id="2", ext_id="B456", label="Item 2")
        ]

        result = self.service.search("test-query")
        self.assertEqual(result, expected_result)

    @patch("ina_ground_control.services.plugins.plugin_service_autocomplete.requests.get")
    def test_search_empty_response(self, mock_get):
        """Test the `search` method with an empty response."""
        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.content = json.dumps([]).encode("utf-8")
        mock_get.return_value = mock_response

        result = self.service.search("test-query")
        self.assertEqual(result, [])


    def test_parse_valid_json(self):
        """Test the `parse` method with a valid JSON response."""
        # Mock response
        mock_response = Mock()
        mock_response.content = json.dumps([
            {"id": "1", "code": "A123", "label": "Item 1"},
            {"id": "2", "code": "B456", "label": "Item 2"}
        ]).encode("utf-8")

        # Expected result
        expected_result = [
            PluginAutocompleteValueDTO(id="1", ext_id="A123", label="Item 1"),
            PluginAutocompleteValueDTO(id="2", ext_id="B456", label="Item 2")
        ]

        result = self.service.parse(mock_response)
        self.assertEqual(result, expected_result)

    def test_parse_empty_json(self):
        """Test the `parse` method with an empty JSON response."""
        # Mock response
        mock_response = Mock()
        mock_response.content = json.dumps([]).encode("utf-8")

        result = self.service.parse(mock_response)
        self.assertEqual(result, [])

    def test_parse_unknown_data_type(self):
        #Test the `parse` method with an unknown data type.
        self.service.config.data_type = "xml"  # Unsupported data type

        mock_response = Mock()

        with self.assertRaises(ValueError):
            self.service.parse(mock_response)

if __name__ == "__main__":
    unittest.main()
