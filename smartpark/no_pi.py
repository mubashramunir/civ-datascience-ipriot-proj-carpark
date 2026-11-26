
"""Launch the Smart Carpark graphical application."""

import tkinter as tk

from smartpark.carpark_manager import CarparkManager
from smartpark.carpark_display import CarParkDisplay
from smartpark.car_detector import CarDetectorWindow


if __name__ == '__main__':
    root = tk.Tk()

    # Create the real carpark manager.
    manager = CarparkManager("samples_and_snippets/config.json")

    # Connect the display to the manager.
    display = CarParkDisplay(root)
    display.data_provider = manager
    manager.add_update_callback(display.update_display)

    # Connect the sensor simulator to the manager.
    detector = CarDetectorWindow(root)
    detector.add_listener(manager)

    root.mainloop()
