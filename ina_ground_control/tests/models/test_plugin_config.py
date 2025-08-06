"""Unit tests for plugin config """
# pylint: disable=redefined-outer-name
import unittest
from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase
from ina_ground_control.models.plugin.plugin_config import PluginConfigDTO, TYPE_MAPPING
from ina_ground_control.models.plugin.plugin_base import PluginConfigType

class TestPluginConfigDTO(unittest.TestCase):
    """Set up test data."""
    def setUp(self):
        self.valid_data = {
            "type": PluginConfigType.GET_PLUGIN,
            "search_query": "title",
            "search_query_param": "q",
            "search_item_sort": "title,asc",
            "response_id_key": "id",  # Add this
            "response_ext_id_key": "ext_id",  # Add this
            "response_label_key": "label",  # Add this
        }
        self.invalid_data = {
            "search_query": "title",  # Missing "type" field
        }
        self.unknown_type_data = {
            "type": "unknown_plugin",
            "some_field": "value",
        }

    def test_build_with_valid_data(self):
        """Test build method with valid data."""

        result = PluginConfigDTO.build(self.valid_data)

        # Verify that the result is an instance of PluginConfigAutoComplete
        self.assertIsInstance(result, PluginConfigAutoComplete)

        # Check that attributes are parsed correctly
        self.assertEqual(result.search_query, self.valid_data["search_query"])
        self.assertEqual(result.response_id_key, self.valid_data["response_id_key"])

    def test_build_with_missing_type_field(self):
        """Test build method when 'type' field is missing."""
        with self.assertRaises(ValueError) as context:
            PluginConfigDTO.build(self.invalid_data)
        self.assertEqual(
            str(context.exception),
            'The "type" field is required to determine the correct subtype.',
        )

    def test_build_with_unknown_type(self):
        """Test build method with a type not in TYPE_MAPPING."""
        result = PluginConfigDTO.build(self.unknown_type_data)

        # Ensure that the result is the original data (not transformed)
        self.assertEqual(result, self.unknown_type_data)

    def test_type_mapping_consistency(self):
        """Ensure TYPE_MAPPING contains valid targets."""
        for _, target_class in TYPE_MAPPING.items():
            self.assertTrue(issubclass(target_class, PluginConfigBase))

