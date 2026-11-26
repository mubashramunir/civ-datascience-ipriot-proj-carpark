
"""Defines a car parked in the Smart Carpark."""

from datetime import datetime


class Car:
    """Represents a vehicle entering and leaving the carpark."""

    def __init__(self, license_plate: str, model: str = "Unknown"):
        """Initialise a car with its registration and model."""
        self.license_plate = license_plate
        self.model = model
        self.entry_time = datetime.now()
        self.exit_time = None

    def record_exit(self):
        """Record the time when the car leaves the carpark."""
        self.exit_time = datetime.now()

    def __str__(self):
        """Return a readable description of the car."""
        return f"{self.license_plate} - {self.model}"
