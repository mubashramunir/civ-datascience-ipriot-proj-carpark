
"""GUI display components for the Smart Carpark."""

import time
import tkinter as tk
from typing import Iterable

from smartpark.interfaces import CarparkDataProvider


class WindowedDisplay:
    """Display a set of fields and their values in a GUI window."""

    DISPLAY_INIT = '– – –'
    SEP = ':'

    def __init__(self, root, title: str, display_fields: Iterable[str]):
        """Create a Tkinter window with the specified display fields."""
        self.window = tk.Toplevel(root)
        self.window.title(f'{title}: Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}

        for i, field in enumerate(self.display_fields):

            # Create the field and value labels.
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window,
                text=field + self.SEP,
                font=('Arial', 50)
            )

            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window,
                text=self.DISPLAY_INIT,
                font=('Arial', 50)
            )

            # Position the labels inside the display window.
            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5
            )

            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10
            )

    def show(self):
        """Show the display without starting another event loop."""
        self.window.deiconify()

    def update(self, updated_values: dict):
        """Update the displayed values using a dictionary."""
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')

                field_name = self.gui_elements[field].cget(
                    'text'
                ).rstrip(self.SEP)

                self.gui_elements[field_value].configure(
                    text=updated_values[field_name]
                )


class CarParkDisplay:
    """Display the current status of the Smart Carpark."""

    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self, root):
        """Initialise the carpark display."""
        self.root = root
        self._provider = None

        self.window = WindowedDisplay(
            root, 'Moondalup', CarParkDisplay.fields
        )
        self.window.show()

        # Schedule display updates without blocking the GUI.
        self.root.after(1000, self.check_updates)

    @property
    def data_provider(self):
        """Return the current carpark data provider."""
        return self._provider

    @data_provider.setter
    def data_provider(self, provider):
        """Connect a valid carpark data provider."""
        if isinstance(provider, CarparkDataProvider):
            self._provider = provider

    def update_display(self):
        """Update available bays, temperature and current time."""
        # Skip updates if the display has been closed.
        if not self.window.window.winfo_exists():
            return

        if self._provider is None:
            return

        field_values = dict(zip(CarParkDisplay.fields, [
            f'{self._provider.available_spaces:03d}',
            f'{self._provider.temperature:.1f}℃',
            time.strftime("%H:%M:%S", self._provider.current_time)
        ]))

        self.window.update(field_values)

    def check_updates(self):
        """Refresh the display every second."""
        # Stop scheduled refreshes if the display has been closed.
        if not self.window.window.winfo_exists():
            return

        self.update_display()

        # Schedule the next refresh after one second.
        self.root.after(1000, self.check_updates)
