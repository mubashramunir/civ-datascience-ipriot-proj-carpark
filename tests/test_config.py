
"""Automated tests for the carpark configuration parser."""

import unittest
from pathlib import Path

from smartpark.config_parser import parse_config


class TestConfigParsing(unittest.TestCase):
    """Verify that the carpark configuration is loaded correctly."""

    def test_parse_config_has_correct_location_and_spaces(self):
        """Check the location and total parking capacity."""
        # Arrange
        config_file = (
            Path(__file__).resolve().parent.parent
            / "samples_and_snippets"
            / "config.json"
        )

        # Act
        parking_lot = parse_config(config_file)

        # Assert
        self.assertEqual(parking_lot["location"], "moondalup")
        self.assertEqual(parking_lot["total-spaces"], 130)


if __name__ == "__main__":
    unittest.main()
