
"""Automated tests for the Car class."""

import unittest
from datetime import datetime

from smartpark.car import Car


class TestCar(unittest.TestCase):
    """Verify vehicle creation and timestamp recording."""

    def test_car_creation(self):
        """Check that a car stores its licence plate and model."""
        car = Car("ABC123", "Toyota Corolla")

        self.assertEqual(car.license_plate, "ABC123")
        self.assertEqual(car.model, "Toyota Corolla")

    def test_default_model(self):
        """Check the default model when none is provided."""
        car = Car("ABC123")

        self.assertEqual(car.model, "Unknown")

    def test_entry_timestamp(self):
        """Check that the entry timestamp is recorded automatically."""
        before = datetime.now()
        car = Car("ABC123")
        after = datetime.now()

        self.assertIsInstance(car.entry_time, datetime)
        self.assertGreaterEqual(car.entry_time, before)
        self.assertLessEqual(car.entry_time, after)

    def test_initial_exit_timestamp(self):
        """Check that a newly parked car has no exit timestamp."""
        car = Car("ABC123")

        self.assertIsNone(car.exit_time)

    def test_record_exit(self):
        """Check that the exit timestamp is recorded correctly."""
        car = Car("ABC123")
        car.record_exit()

        self.assertIsInstance(car.exit_time, datetime)
        self.assertGreaterEqual(car.exit_time, car.entry_time)

    def test_string_representation(self):
        """Check the readable description of a car."""
        car = Car("ABC123", "Toyota Corolla")

        self.assertEqual(str(car), "ABC123 - Toyota Corolla")


if __name__ == "__main__":
    unittest.main()
