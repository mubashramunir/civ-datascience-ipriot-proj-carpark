
"""Car detection GUI for the Smart Carpark."""

import tkinter as tk

from smartpark.interfaces import CarparkSensorListener


class CarDetectorWindow:
    """Simulate vehicle detection and temperature sensor events."""

    def __init__(self, root):
        """Initialise the car detector window and input controls."""
        self.root = root
        self.root.title("Car Detector ULTRA")
        self.listeners = []

        # Create the incoming vehicle button.
        self.btn_incoming_car = tk.Button(
            self.root,
            text='🚘 Incoming Car',
            font=('Arial', 50),
            cursor='right_side',
            command=self.incoming_car
        )
        self.btn_incoming_car.grid(
            padx=10, pady=5, row=0, columnspan=2
        )

        # Create the outgoing vehicle button.
        self.btn_outgoing_car = tk.Button(
            self.root,
            text='Outgoing Car 🚘',
            font=('Arial', 50),
            cursor='bottom_left_corner',
            command=self.outgoing_car
        )
        self.btn_outgoing_car.grid(
            padx=10, pady=5, row=1, columnspan=2
        )

        # Create the temperature input controls.
        self.temp_label = tk.Label(
            self.root,
            text="Temperature",
            font=('Arial', 20)
        )
        self.temp_label.grid(
            padx=10, pady=5, column=0, row=2
        )

        self.temp_var = tk.StringVar()

        # Detect changes to the temperature input.
        self.temp_var.trace_add(
            "write", lambda *args: self.handle_temperature_input()
        )

        self.temp_box = tk.Entry(
            self.root,
            font=('Arial', 20),
            textvariable=self.temp_var
        )
        self.temp_box.grid(
            padx=10, pady=5, column=1, row=2
        )

        # Create the licence plate input controls.
        self.plate_label = tk.Label(
            self.root,
            text="License Plate",
            font=('Arial', 20)
        )
        self.plate_label.grid(
            padx=10, pady=5, column=0, row=3
        )

        self.plate_var = tk.StringVar()

        self.plate_box = tk.Entry(
            self.root,
            font=('Arial', 20),
            textvariable=self.plate_var
        )
        self.plate_box.grid(
            padx=10, pady=5, column=1, row=3
        )

    @property
    def current_license(self):
        """Return the licence plate entered by the user."""
        return self.plate_var.get()

    def add_listener(self, listener):
        """Register a valid carpark sensor listener."""
        if isinstance(listener, CarparkSensorListener):
            self.listeners.append(listener)

    def incoming_car(self):
        """Notify listeners when a car enters."""
        for listener in self.listeners:
            listener.incoming_car(self.current_license)

    def outgoing_car(self):
        """Notify listeners when a car exits."""
        for listener in self.listeners:
            listener.outgoing_car(self.current_license)

    def handle_temperature_input(self):
        """Read the temperature input and forward valid readings."""
        try:
            temperature = float(self.temp_var.get())
        except ValueError:
            return

        self.temperature_changed(temperature)

    def temperature_changed(self, temp):
        """Notify listeners of a new temperature reading."""
        print(f"GUI temperature event received: {temp}")

        for listener in self.listeners:
            listener.temperature_reading(temp)
