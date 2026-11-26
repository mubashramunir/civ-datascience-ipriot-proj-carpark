
"""Automated tests for the CarparkManager class."""

import json
import logging
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from smartpark.carpark_manager import CarparkManager


class TestCarparkManager(unittest.TestCase):
    """Verify parking management and vehicle events."""

    def setUp(self):
        """Create a temporary configuration before each test."""
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.config_file = Path(self.temp_dir.name) / "config.json"

        config = {
            "CarParks": [
                {
                    "name": "test-carpark",
                    "total-spaces": 2,
                    "total-cars": 0,
                    "location": "test-location"
                }
            ]
        }

        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(config, file)

        # Store test activity in a temporary log file.
        self.log_file = Path(self.temp_dir.name) / "test_activity.log"

        logger = logging.getLogger("smartpark.carpark")
        self.addCleanup(self.restore_logger, logger, logger.handlers[:])
        logger.handlers = []

        original_handler = logging.FileHandler

        with patch(
            "smartpark.carpark_manager.logging.FileHandler",
            side_effect=lambda *args, **kwargs: original_handler(
                self.log_file, encoding="utf-8"
            )
        ):
            self.manager = CarparkManager(self.config_file)

    def restore_logger(self, logger, original_handlers):
        """Close temporary log handlers and restore the original ones."""
        for handler in logger.handlers:
            handler.close()

        logger.handlers = original_handlers

    def test_fresh_carpark(self):
        """Check the initial carpark configuration."""
        self.assertEqual(self.manager.available_spaces, 2)
        self.assertEqual(self.manager.location, "test-location")
        self.assertEqual(self.manager.name, "test-carpark")
        self.assertEqual(len(self.manager.cars), 0)

    def test_incoming_car(self):
        """Check that an incoming car occupies a parking space."""
        self.manager.incoming_car("ABC123")

        self.assertEqual(self.manager.available_spaces, 1)
        self.assertIn("ABC123", self.manager.cars)

    def test_duplicate_entry(self):
        """Check that duplicate entries do not occupy extra spaces."""
        self.manager.incoming_car("ABC123")
        self.manager.incoming_car("ABC123")

        self.assertEqual(self.manager.available_spaces, 1)
        self.assertEqual(len(self.manager.cars), 1)

    def test_outgoing_car(self):
        """Check that an outgoing car releases a parking space."""
        self.manager.incoming_car("ABC123")
        car = self.manager.cars["ABC123"]

        self.manager.outgoing_car("ABC123")

        self.assertEqual(self.manager.available_spaces, 2)
        self.assertNotIn("ABC123", self.manager.cars)
        self.assertIsNotNone(car.exit_time)

    def test_unknown_car_exit(self):
        """Check that an unknown car cannot release a space."""
        self.manager.incoming_car("ABC123")
        self.manager.outgoing_car("XYZ999")

        self.assertEqual(self.manager.available_spaces, 1)
        self.assertEqual(len(self.manager.cars), 1)

    def test_full_carpark(self):
        """Check that additional cars are rejected at full capacity."""
        self.manager.incoming_car("ABC123")
        self.manager.incoming_car("XYZ999")

        self.assertEqual(self.manager.available_spaces, 0)

        self.manager.incoming_car("TEST123")

        self.assertEqual(self.manager.available_spaces, 0)
        self.assertEqual(len(self.manager.cars), 2)
        self.assertNotIn("TEST123", self.manager.cars)

    def test_empty_license_plate(self):
        """Check that empty licence plates are rejected."""
        self.manager.incoming_car("")
        self.manager.incoming_car("   ")

        self.assertEqual(self.manager.available_spaces, 2)
        self.assertEqual(len(self.manager.cars), 0)

    def test_license_plate_normalisation(self):
        """Check that licence plates are standardised."""
        self.manager.incoming_car(" abc123 ")

        self.assertIn("ABC123", self.manager.cars)
        self.assertEqual(self.manager.available_spaces, 1)

    def test_initial_temperature(self):
        """Check the initial temperature reading."""
        self.assertEqual(self.manager.temperature, 0)

    def test_valid_temperature(self):
        """Check that valid temperature readings are stored."""
        self.manager.temperature_reading("26.5")

        self.assertEqual(self.manager.temperature, 26.5)

    def test_invalid_temperature(self):
        """Check that invalid readings preserve the temperature."""
        self.manager.temperature_reading(25.5)
        self.manager.temperature_reading("abc")

        self.assertEqual(self.manager.temperature, 25.5)

    def test_incoming_car_callback(self):
        """Check that a successful entry triggers a callback."""
        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.incoming_car("ABC123")

        self.assertEqual(len(updates), 1)

    def test_duplicate_entry_no_callback(self):
        """Check that a duplicate entry does not trigger a callback."""
        self.manager.incoming_car("ABC123")

        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.incoming_car("ABC123")

        self.assertEqual(len(updates), 0)

    def test_outgoing_car_callback(self):
        """Check that a successful exit triggers a callback."""
        self.manager.incoming_car("ABC123")

        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.outgoing_car("ABC123")

        self.assertEqual(len(updates), 1)

    def test_unknown_exit_no_callback(self):
        """Check that an unknown exit does not trigger a callback."""
        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.outgoing_car("XYZ999")

        self.assertEqual(len(updates), 0)

    def test_temperature_callback(self):
        """Check that a valid temperature triggers a callback."""
        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.temperature_reading(26.5)

        self.assertEqual(len(updates), 1)

    def test_invalid_temperature_no_callback(self):
        """Check that an invalid reading does not trigger a callback."""
        updates = []
        self.manager.add_update_callback(
            lambda: updates.append("updated")
        )

        self.manager.temperature_reading("abc")

        self.assertEqual(len(updates), 0)

    def test_multiple_manager_instances(self):
        """Check that multiple managers initialise correctly."""
        handler_count = len(self.manager.logger.handlers)

        second_manager = CarparkManager(self.config_file)

        self.assertEqual(second_manager.available_spaces, 2)
        self.assertIs(self.manager.logger, second_manager.logger)
        self.assertEqual(
            len(second_manager.logger.handlers), handler_count
        )

        self.manager.incoming_car("ABC123")

        self.assertEqual(self.manager.available_spaces, 1)
        self.assertEqual(second_manager.available_spaces, 2)

    def test_entry_logging(self):
        """Check that vehicle entry is recorded with a timestamp."""
        self.manager.incoming_car("ABC123")

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("Car entered: ABC123", log_content)
        self.assertRegex(
            log_content,
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        )

    def test_exit_logging(self):
        """Check that vehicle exit is recorded with a timestamp."""
        self.manager.incoming_car("ABC123")
        self.manager.outgoing_car("ABC123")

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("Car exited: ABC123", log_content)
        self.assertRegex(
            log_content,
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            r".*Car exited: ABC123"
        )

    def test_duplicate_entry_logging(self):
        """Check that rejected duplicate entries are recorded."""
        self.manager.incoming_car("ABC123")
        self.manager.incoming_car("ABC123")

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn(
            "Duplicate entry rejected: ABC123", log_content
        )

    def test_unknown_exit_logging(self):
        """Check that rejected unknown exits are recorded."""
        self.manager.outgoing_car("XYZ999")

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn(
            "Unknown exit rejected: XYZ999", log_content
        )

    def test_temperature_logging(self):
        """Check that temperature updates are recorded."""
        self.manager.temperature_reading(26.5)

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("Temperature updated: 26.5 C", log_content)


if __name__ == "__main__":
    unittest.main()
