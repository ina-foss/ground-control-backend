import unittest

from ina_ground_control.models.plugin.plugin_autocomplete import PluginConfigAutoComplete
from ina_ground_control.models.plugin.plugin_base import PluginConfigBase
from models.plugin.plugin_config import PluginConfigDTO, TYPE_MAPPING


class TestPluginConfigDTO(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            "type": "plugin_autocomplete",
            "search_attr": "title",
            "search_query_param": "q",
            "search_item_size": 10,
            "search_item_sort": "title,asc",
        }
        self.invalid_data = {
            "search_attr": "title",  # Missing "type" field
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
        self.assertEqual(result.search_attr, self.valid_data["search_attr"])
        self.assertEqual(result.search_item_size, self.valid_data["search_item_size"])

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
        for plugin_type, target_class in TYPE_MAPPING.items():
            self.assertTrue(issubclass(target_class, PluginConfigBase))


if __name__ == "__main__":
    unittest.main()
