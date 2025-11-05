"""Unit tests for Plugin autocomplete services"""

# pylint: disable=redefined-outer-name
import json
import unittest
from unittest.mock import Mock, patch

from requests.models import Response

from ina_ground_control.exception.exceptions import GroundControlException
from ina_ground_control.models.plugin.plugin_autocomplete import (
    PluginConfigAutoComplete,
)
from ina_ground_control.models.plugin.plugin_autocomplete_value_dto import (
    PluginAutocompleteValueDTO,
)
from ina_ground_control.models.plugin.plugin_base import DataTypeEnum, PluginConfigType
from ina_ground_control.services.plugins.plugin_service_autocomplete import (
    PluginServiceAutoComplete,
)

mock_autocomplete_response = json.dumps(
    {
        "@context": "https://www.iptc.org/std/IKOS/IKOS.jsonld",
        "uri": "https://cv.iptc.org/newscodes/mediatopic/",
        "type": "https://www.w3.org/2004/02/skos/core#ConceptScheme",
        "prefSchemeAlias": "medtop",
        "authority": "https://www.iptc.org",
        "copyrightHolder": "IPTC, International Press Telecommunications Council - https://iptc.org",
        "licenceLink": "https://creativecommons.org/licenses/by/4.0/",
        "dateReleased": "2024-11-05T12:00:00+00:00",
        "prefLabel": {},
        "definition": {},
        "note": {},
        "hasTopConcept": [
            "https://cv.iptc.org/newscodes/mediatopic/01000000",
            "https://cv.iptc.org/newscodes/mediatopic/02000000",
            "https://cv.iptc.org/newscodes/mediatopic/03000000",
            "https://cv.iptc.org/newscodes/mediatopic/04000000",
            "https://cv.iptc.org/newscodes/mediatopic/05000000",
            "https://cv.iptc.org/newscodes/mediatopic/06000000",
            "https://cv.iptc.org/newscodes/mediatopic/07000000",
            "https://cv.iptc.org/newscodes/mediatopic/08000000",
            "https://cv.iptc.org/newscodes/mediatopic/09000000",
            "https://cv.iptc.org/newscodes/mediatopic/10000000",
            "https://cv.iptc.org/newscodes/mediatopic/11000000",
            "https://cv.iptc.org/newscodes/mediatopic/12000000",
            "https://cv.iptc.org/newscodes/mediatopic/13000000",
            "https://cv.iptc.org/newscodes/mediatopic/14000000",
            "https://cv.iptc.org/newscodes/mediatopic/15000000",
            "https://cv.iptc.org/newscodes/mediatopic/16000000",
            "https://cv.iptc.org/newscodes/mediatopic/17000000",
        ],
        "conceptSet": [
            {
                "uri": "https://cv.iptc.org/newscodes/mediatopic/01000000",
                "qcode": "medtop:01000000",
                "type": ["https://www.w3.org/2004/02/skos/core#Concept"],
                "inScheme": ["https://cv.iptc.org/newscodes/mediatopic/"],
                "modified": "2021-02-18T12:00:00+00:00",
                "prefLabel": {"fr": "Arts, culture, divertissement et médias"},
                "definition": {
                    "fr": "Toutes les formes d'arts, de divertissement, de culture et de médias"
                },
                "narrower": ["medtop:20000002", "medtop:20000038", "medtop:20000045"],
                "exactMatch": ["https://cv.iptc.org/newscodes/subjectcode/01000000"],
                "created": "2009-10-22T02:00:00+00:00",
            },
            {
                "uri": "https://cv.iptc.org/newscodes/mediatopic/02000000",
                "qcode": "medtop:02000000",
                "type": ["https://www.w3.org/2004/02/skos/core#Concept"],
                "inScheme": ["https://cv.iptc.org/newscodes/mediatopic/"],
                "modified": "2021-05-05T12:00:00+00:00",
                "prefLabel": {"fr": "Criminalité, droit et justice"},
                "definition": {},
                "narrower": [
                    "medtop:20000082",
                    "medtop:20000106",
                    "medtop:20000119",
                    "medtop:20000121",
                    "medtop:20000129",
                ],
                "exactMatch": [
                    "https://cv.iptc.org/newscodes/subjectcode/02000000",
                    "https://www.wikidata.org/entity/Q146491",
                ],
                "created": "2009-10-22T02:00:00+00:00",
            },
        ],
    }
).encode("utf-8")


class TestPluginServiceAutoComplete(unittest.TestCase):
    """Unit tests for the PluginServiceAutoComplete class."""

    def setUp(self):
        self.config = PluginConfigAutoComplete(
            data_source="https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
            search_query="id",
            data_type=DataTypeEnum.JSON,
            type=PluginConfigType.PLUGIN_REQUEST_GET,
            response_id_key="$.conceptSet[*].qcode",
            response_ext_id_key="$.conceptSet[*].uri",
            response_label_key="$.conceptSet[*].prefLabel.fr",
        )
        self.service = PluginServiceAutoComplete(config=self.config)

    @patch(
        "ina_ground_control.services.plugins.plugin_service_autocomplete.requests.get"
    )
    def test_search_empty_response(self, mock_get):
        """Test the `search` method with an empty response."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.content = json.dumps([]).encode("utf-8")
        mock_get.return_value = mock_response

        result = self.service.search("test-query")
        self.assertEqual(result, [])

    def test_parse_valid_json_with_id(self):
        # Test the `parse` method with a valid JSON response.
        self.config = PluginConfigAutoComplete(
            data_source="https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
            search_query="query",
            data_type=DataTypeEnum.JSON,
            type=PluginConfigType.PLUGIN_REQUEST_GET,
            response_id_key="$[*].id",
            response_ext_id_key="$[*].code",
            response_label_key="$[*].label",
        )
        self.service = PluginServiceAutoComplete(config=self.config)

        mock_response = Mock()
        mock_response.content = json.dumps(
            [
                {"id": "1", "code": "A123", "label": "Item 1"},
                {"id": "2", "code": "B456", "label": "Item 2"},
            ]
        ).encode("utf-8")

        # Expected result
        expected_result = [
            PluginAutocompleteValueDTO(id="1", ext_id="A123", label="Item 1"),
            PluginAutocompleteValueDTO(id="2", ext_id="B456", label="Item 2"),
        ]

        result = self.service.parse(mock_response)
        self.assertEqual(result, expected_result)

    def test_parse_valid_json(self):
        # Test the `parse` method with a valid JSON response.
        mock_response = Mock()
        mock_response.content = mock_autocomplete_response
        # Expected result
        expected_result = [
            PluginAutocompleteValueDTO(
                id="medtop:01000000",
                ext_id="https://cv.iptc.org/newscodes/mediatopic/01000000",
                label="Arts, culture, divertissement et médias",
            ),
            PluginAutocompleteValueDTO(
                id="medtop:02000000",
                ext_id="https://cv.iptc.org/newscodes/mediatopic/02000000",
                label="Criminalité, droit et justice",
            ),
        ]

        result = self.service.parse(mock_response)
        self.assertEqual(result, expected_result)

    def test_parse_empty_json(self):
        """Test the `parse` method with an empty JSON response."""
        mock_response = Mock()
        mock_response.content = json.dumps([]).encode("utf-8")

        result = self.service.parse(mock_response)
        self.assertEqual(result, [])

    def test_parse_unknown_data_type(self):
        """Test the `parse` method with an unknown data type."""
        self.service.config.data_type = "xml"  # Unsupported data type

        mock_response = Mock()

        with self.assertRaises(GroundControlException):
            self.service.parse(mock_response)
