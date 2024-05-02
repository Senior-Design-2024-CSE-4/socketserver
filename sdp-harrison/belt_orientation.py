#! /usr/bin/env python
# encoding: utf-8
import time
from datetime import datetime
from datetime import timedelta
from threading import Event, Lock

from examples_utility import belt_controller_log_to_stdout, interactive_belt_connection
from pybelt.belt_controller import BeltController, BeltConnectionState, BeltControllerDelegate

# Event to stop the script
button_pressed_event = Event()

# Belt orientation
orientation_lock = Lock()  # Lock to read and write the heading and period (only necessary for BLE interface)
belt_heading: int = -1  # Last known belt heading value
belt_orientation_update_period = timedelta()  # Period between the last two orientation updates


class Delegate(BeltControllerDelegate):

    def __init__(self):
        # __init__ is only used for the orientation notification period
        self._last_orientation_update_time = datetime.now()  # Time of the last heading update

    def on_belt_orientation_notified(self, heading, is_orientation_accurate, extra):
        global belt_heading
        global belt_orientation_update_period
        with orientation_lock:
            belt_heading = heading
            # Below code is only for measuring notification period
            now = datetime.now()
            belt_orientation_update_period = now - self._last_orientation_update_time
            self._last_orientation_update_time = now

    def on_belt_button_pressed(self, button_id, previous_mode, new_mode):
        button_pressed_event.set()


def set_orientation_notification_period(belt_controller, period, start_notification) -> bool:
    """
    Sets the period for orientation notifications.
    :param belt_controller: The belt controller.
    :param period: The period in seconds.
    :param start_notification: 'True' to start the orientation notification.
    :return: 'True' on success, 'False' otherwise.
    """
    if belt_controller.get_connection_state() != BeltConnectionState.CONNECTED:
        print("No belt belt connected to set notification period.")
        return False
    if period < 0.02:
        print("Notification period not supported.")
        return False
    period_ms = int(period*1000.0)
    belt_controller.set_orientation_notifications(False)
    if belt_controller.write_gatt(belt_controller._gatt_profile.param_request_char,
                                  bytes([
                                    0x11,
                                    0x0F,
                                    0x00,
                                    period_ms & 0xFF,
                                    (period_ms >> 8) & 0xFF,
                                  ]),
                                  belt_controller._gatt_profile.param_notification_char,
                                  b'\x10\x0F') != 0:
        print("Failed to write notification period parameter.")
        return False
    return belt_controller.set_orientation_notifications(True)


def main():
    belt_controller_log_to_stdout()

    # Interactive script to connect the belt
    belt_controller_delegate = Delegate()
    belt_controller = BeltController(belt_controller_delegate)
    interactive_belt_connection(belt_controller)
    if belt_controller.get_connection_state() != BeltConnectionState.CONNECTED:
        print("Connection failed.")
        return 0

    # Change orientation notification period
    if not set_orientation_notification_period(belt_controller, 0.02, True):
        print("Failed to change orientation notification period.")
        belt_controller.disconnect_belt()
        return 0

    print("Press a button on the belt to quit.")
    while belt_controller.get_connection_state() == BeltConnectionState.CONNECTED and not button_pressed_event.is_set():
        # Delay for terminal display (not necessary if other processing)
        time.sleep(0.005)
        # Retrieve orientation with lock
        with orientation_lock:
            heading = belt_heading
            notification_period = belt_orientation_update_period.total_seconds()
        # Process orientation
        print("\rBelt heading: {}°\t (period: {:.3f}s)            ".format(heading, notification_period), end="")

    belt_controller.set_orientation_notifications(False)
    belt_controller.disconnect_belt()
    return 0


if __name__ == "__main__":
    main()
