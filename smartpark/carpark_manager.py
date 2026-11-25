
"""Manage vehicles and parking spaces in the Smart Carpark."""

import logging
from datetime import datetime

from smartpark.car import Car
from smartpark.config_parser import parse_config
from smartpark.interfaces import (
    CarparkDataProvider,
    CarparkSensorListener,
)


class CarparkManager(CarparkSensorListener, CarparkDataProvider):
    """Manage the carpark and provide data to the display."""

    def __init__(self, config_file):
        """Load the carpark configuration and initialise its state."""
        config = parse_config(config_file)

        self.location = config["location"]
        self.name = config["name"]
        self.total_spaces = config["total-spaces"]

        self.cars = {}
        self._temperature = 0
        self._update_callbacks = []
        self.logger = logging.getLogger("smartpark.carpark")

        # Prevent duplicate logging handlers.
        if not self.logger.handlers:
            handler = logging.FileHandler(
                "carpark_activity.log", encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def add_update_callback(self, callback):
        """Register a callback for carpark data updates."""
        self._update_callbacks.append(callback)

    def notify_updates(self):
        """Notify registered callbacks when carpark data changes."""
        for callback in self._update_callbacks:
            callback()

    @property
    def available_spaces(self):
        """Return the number of unoccupied parking spaces."""
        return self.total_spaces - len(self.cars)

    @property
    def temperature(self):
        """Return the latest temperature reading."""
        return self._temperature

    @property
    def current_time(self):
        """Return the current local time."""
        return datetime.now().timetuple()

    def incoming_car(self, license_plate):
        """Register a car entering if a parking space is available."""
        if not license_plate or not license_plate.strip():
            print("Error: Licence plate cannot be empty.")
            return

        # Standardise the licence plate before checking it.
        license_plate = license_plate.strip().upper()

        if license_plate in self.cars:
            print(f"Error: Car {license_plate} is already parked.")
            self.logger.warning(
                "Duplicate entry rejected: %s", license_plate
            )
            return

        if self.available_spaces == 0:
            print("Error: Carpark is full.")
            return

        car = Car(license_plate)
        self.cars[license_plate] = car
        self.logger.info("Car entered: %s", license_plate)

        print(f"Car {license_plate} entered successfully.")
        print(f"Available spaces: {self.available_spaces}")

        # Notify the display after a successful entry.
        self.notify_updates()

    def outgoing_car(self, license_plate):
        """Register a car leaving the carpark."""
        if not license_plate or not license_plate.strip():
            print("Error: Licence plate cannot be empty.")
            return

        license_plate = license_plate.strip().upper()

        if license_plate not in self.cars:
            print(f"Error: Car {license_plate} is not in the carpark.")
            self.logger.warning(
                "Unknown exit rejected: %s", license_plate
            )
            return

        # Record the exit time before removing the vehicle.
        car = self.cars[license_plate]
        car.record_exit()

        del self.cars[license_plate]
        self.logger.info("Car exited: %s", license_plate)

        print(f"Car {license_plate} exited successfully.")
        print(f"Available spaces: {self.available_spaces}")
        self.notify_updates()

    def temperature_reading(self, reading):
        """Store a new temperature reading."""
        try:
            temperature = float(reading)
        except (ValueError, TypeError):
            print("Error: Invalid temperature reading.")
            return

        self._temperature = temperature
        self.logger.info("Temperature updated: %.1f C", temperature)

        print(f"Temperature updated to {temperature}°C")
        self.notify_updates()
