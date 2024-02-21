# this version of the code includes modifications that allow a 50 Hz update rate of belt compass value

# TO DO
#   CREATE A new environment to see if I have steps down SAVE IT AS BASECODE???? - 
#   Create a new version with Threading
#   set this up in its own thread so can have constant updating and event monitoring
#     TUTORIAL ON LOCKING   
#          https://www.youtube.com/watch?v=A_Z1lgZLSNc
#          https://www.youtube.com/watch?v=F3-bJlYWeJc
#   need to add handling for belt not being detected (i.e. what happens if belt not connected ... want it to keep trying to connect)

########################################
# VIRTUAL ENVIRONMENT SETUP INSTRUCTIONS
########################################
# setup from https://www.youtube.com/watch?v=mQGgWnJorw4
#open folder in vscode
#add new file xxx.py
#open terminal window with command prompt # RUN ALL FOLLOWING CODE VIA CMD
#CREATE A PYTHON VIRTUAL ENV
#CODE: python -m venv nameofvirtualenv
# e.g. #CODE: python -m venv ve_pybelt  
# make sure using virtual environment interpreter via command palette
#need to tell system that we just want to work inside virtual environment
#CODE: nameofvirtualenv\Scripts\activate   #when do this expect to see parentheses showing rthat are in virtual env
#CODE: pybelt_base_testing\Scripts\activate
#CODE: pip3 install --upgrade pip  
#CODE: pip install xsensdeviceapi-2022.0.0-cp39-none-win_amd64.whl #this file must be local
#CODE: pip install pybelt
#CODE: pip install pyserial
# RUN by right clicking on xxx.py (main) file and select "Run File in Terminal"
#    ... while cmd is selected as the terminal process

#########################################
# NOTES/WARNINGS ON 50 Hz Compass Update
#########################################
# this version of the code includes modifications that allow a 50 Hz update rate ... the modification only works if the firmware update has been installed by putting file NaviBelt_firmware_VARTA_V52_factoryImage.bin only the belt
#   The minimum notification period supported by the belt is 20ms (i.e. 50Hz).
#   Changing the notification period has not been extensively tested and could result in unexpected behavior for small notification periods.
#   It is not recommended to use short notification period over BLE connection.
#   For short notification periods, after disconnection, it may be required to wait a few seconds to reconnect the belt again. If the reconnection failed, it may be necessary to restart the belt.
#   In case the belt does not respond anymore, you can make a “hard power-off” by pressing the power button of the belt more than 6 seconds and then pressing it again to restart the belt.
#   It is important to note that orientation updates from the belt were not designed for updating a system in real-time, just for monitoring and showing on a map the orientation of the belt.
#   In case you need a vibration signal on the belt that is dependent on the orientation, you can use the `vibrate_at_magnetic_bearing` or `send_pulse_command` (with orientation_type=MAGNETIC_BEARING) to get a vibration relative to magnetic North.
#   The belt orientation may be inaccurate when used indoor because of magnetic interference. To get a better orientation, it is recommended to calibrate the belt in the room where it is used (or outdoor if used outdoor).
#   FeelSpace also provides development services: Custom firmware, custom design to fit specific applications/experiments.



#import sys
#print(sys.path)

#import matplotlib
#import xsensdeviceapi
import pybelt
import serial
import time
import threading
import json
import datetime
from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType

# program flags
bOrientationInformation = 1
bBatteryInformation = 1

# program variables
BeltHeading_ThreadShared: int = -1

lock = threading.Lock() # see https://www.youtube.com/watch?v=F3-bJlYWeJc&list=PL7yh-TELLS1F3KytMVZRFO-xIo_S2_Jg1&index=4

# Code to do basic test of whether libraries are installed
#print("XSENS ......................................")
#print(xsensdeviceapi.__name__)
#print("PYBELT ......................................")
#print(pybelt.__spec__)

from pybelt.belt_controller import BeltController, BeltConnectionState, BeltControllerDelegate

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
    ### FIND THE COM PORT THE BELT IS ON (see code examples for additional features)
    from serial.tools import list_ports
    # get available ports
    available_ports = list(serial.tools.list_ports.comports())
    # print available ports to screen
    for p in available_ports:
        print(p.device)
    print(len(available_ports), 'ports found')
    # find the port the belt is on and save the name of that port
    beltport_sn = 'None'
    for port in available_ports:
        print('Serial Num = ', port.serial_number)
        if port.serial_number == "ABCD123456789":
            print(port.name)
            print('Found Serial Num:', port.serial_number, '; Port name', port.name)
            beltport_sn = port.serial_number
            beltport_name = port.name
    if beltport_sn == "None":
        print('WARNING: nothing found')
    print('Found Serial Num:', beltport_sn, '; Port name', beltport_name)

    ##################################################
    # SETUP BELT CONTROLLER and EVENT MANAGEMENT
    ##################################################
    from pybelt.belt_controller import BeltConnectionState
    from threading import Event
    from threading import current_thread
    from pybelt.belt_controller import BeltControllerDelegate
    # set up belt controller so we are able to to get information from that belt thread
    button_pressed_event = Event()
    class Delegate(BeltControllerDelegate):
        def on_belt_orientation_notified(self, heading, is_orientation_accurate, extra):
            if bOrientationInformation == 1:
                #print("\rBelt heading {}°, accurate: {}            ".format(heading, is_orientation_accurate), end="")
                global BeltHeading_ThreadShared
                global lock
                lock.acquire()
                BeltHeading_ThreadShared = heading
                lock.release()
        def on_belt_battery_notified(self, charge_level, extra):
            if bBatteryInformation == 1:
                print("\rBelt battery {}%            ".format(round(charge_level, 2)), end="")
        def on_belt_button_pressed(self, button_id, previous_mode, new_mode):
            button_pressed_event.set()
    belt_controller_delegate = Delegate()

    ###############################
    # CONNECT TO THE BELT
    ###############################
    #from pybelt.belt_controller import *
    from pybelt.belt_controller import BeltController, BeltMode, BeltConnectionState
    #belt_controller = BeltController()
    belt_controller = BeltController(belt_controller_delegate)
    # connect to belt
    belt_controller.connect(beltport_name) 
    # check connection state
    if belt_controller.get_connection_state() == BeltConnectionState.CONNECTED:
        print("Connection successful.")
        print('Connection State = ', belt_controller.get_connection_state())
    else:
        print("Connection failed.")

    ###########################
    # SET BELT MODE (set/check)
    ###########################
    #    STANDBY = 0; WAIT = 1 ; COMPASS = 2; APP_MODE = 3; PAUSE = 4; CALIBRATION = 5; CROSSING = 6
    #       The app-mode is the mode in which the vibration is controlled by the connected device. The app-mode is only accessible when the device is connected. If the device is unexpectedly disconnected in app-mode, the belt switches automatically to the wait mode.
    #       In standby, all components of the belt, including Bluetooth, are switched-off. The belt only reacts to a long press on the power button that starts the belt and put it in wait mode. Since Bluetooth connection is not possible in standby mode, the Bluetooth connection is closed after a notification of the standby mode.
    #       In wait mode, the belt waits for a user input, either a button-press or a command from a connected device. A periodic vibration signal indicates that the belt is active. This wait signal is a single pulse when no device is connected, a double pulse when a device is connected, and a succession of short pulses when the belt is in pairing mode.
    #       In compass mode, the belt vibrates towards magnetic North. From the wait and app modes, the compass mode is obtained by a press on the compass button of the belt.
    #       In crossing mode, the belt vibrates towards an initial heading direction. From the wait and app modes, the crossing mode is obtained by a double press on the compass button of the belt.
    #       In pause mode, the vibration is stopped. From the wait, compass and app modes, the pause mode is obtained by a press on the pause button. Another press on the pause button in pause mode returns to the previous mode. In pause mode, the user can change the (default) vibration intensity by pressing the home button (increase intensity) or compass button (decrease intensity).
    #       The calibration mode is used for the calibration procedure of the belt.
    print("Belt mode: {}".format(belt_controller.get_belt_mode()))
    print("Belt firmware version: {}".format(belt_controller.get_firmware_version()))
    belt_controller.set_belt_mode(BeltMode.APP_MODE)

    #from functs import set_orientation_notification_period
    # Change orientation notification period
    if not set_orientation_notification_period(belt_controller, 0.02, True):
        print("Failed to change orientation notification period.")
        belt_controller.disconnect_belt()
        return 0

    #############################################
    # NOTIFICATIONS FROM BELT CONTROLLER THREAD 
    #############################################
    # ORIENTATION INFORMATION
    if bOrientationInformation == 1:
        belt_controller.set_orientation_notifications(True) # Start orientation notification (should already be started during handshake)
    # BATTERY INFORMATION
    if bBatteryInformation == 1:
        belt_controller.set_power_status_notifications(True) # Start battery notification (should already be started during handshake)



    ##################################
    # GET ORIENTATION NOTIFICATIONS (WITH PRECISION TIMING)
    #################################
    bOrientationNotificationTest = 1

    if bOrientationNotificationTest == 1:
        numsecs4test = 3
        numnanosecs4test = numsecs4test * 1000000000
        t_start_ns = time.perf_counter_ns()
        t_now_ns = t_start_ns
        t_end_ns = t_start_ns + numnanosecs4test
        bFirstIteration = True
        counter = 0
        periodsum = 0
        with open("sample2.json", "w") as outfile:

            while time.perf_counter_ns() < t_end_ns:
                if bFirstIteration == True:
                    bFirstIteration = False 
                    t_prev_ns = t_start_ns 
                t_now_ns = time.perf_counter_ns()
                t_period_ns = t_now_ns - t_prev_ns
                update_freq = 1 / (t_period_ns / 1000000000)
                t_prev_ns = t_now_ns
                counter = counter + 1
                periodsum = periodsum + t_period_ns
                #print("\rPeriod of Process {}s                  ".format(t_period), end="")
                #print("Time (ns) = ",time.perf_counter_ns())
                #print("Period of Process (s) = ",t_period_ns / 1000000000)
                #print("Counter (s) = ",counter)
                from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType, BeltVibrationTimerOption
                if bOrientationNotificationTest == 1:
                    #with open("sample2.json", "a") as outfile:

                    #print("\rBelt heading {}°            ".format(BeltHeading_ThreadShared), end="")
                        lock.acquire()
                        print("Freq (Hz):",round(update_freq),"\t\tBelt heading",BeltHeading_ThreadShared)
                        start_time = time.time()
                        vp1 = 1 # channel index
                        vp2 = BeltVibrationPattern.DOUBLE_LONG # pattern
                        vp3 = 50 # intensity
                        vp4 = BeltOrientationType.ANGLE # orientation_type (MOTOR_INDEX, ANGLE, ...?)
                        vp5 = 0 # orientation,
                        vp6 = 1 # pattern_iterations
                        vp7 = 250 # pattern_period
                        vp8 = 0 # pattern_start_time
                        vp9 = False # exclusive_channel
                        vp10 = False # clear_other_channels
                        belt_controller.send_vibration_command(vp1,vp2,vp3,vp4,BeltHeading_ThreadShared,vp6,vp7,vp8,vp9,vp10)
                        if vp2 == 0:
                            vib_pattern = 'NO VIBRATION'
                        elif vp2 == 1:
                            vib_pattern = 'CONTINUOUS'
                        elif vp2 == 2:
                            vib_pattern == 'SINGLE SHORT'
                        elif vp2 == 3:
                            vib_pattern == 'SINGLE_LONG'
                        elif vp2 == 4:
                            vib_pattern = 'DOUBLE SHORT'
                        else:
                            vib_pattern = 'DOUBLE LONG'
                        if belt_controller.get_belt_mode() == BeltMode.STANDBY:
                            b_mode = "STANDBY"
                        elif belt_controller.get_belt_mode() == BeltMode.WAIT:
                            b_mode = "WAIT"
                        elif belt_controller.get_belt_mode() == BeltMode.COMPASS:
                            b_mode = "COMPASS"
                        elif belt_controller.get_belt_mode() == BeltMode.APP_MODE:
                            b_mode = "APP_MODE"
                        elif belt_controller.get_belt_mode() == BeltMode.PAUSE:
                            b_mode = "PAUSE"
                        elif belt_controller.get_belt_mode() == BeltMode.CALIBRATION:
                            b_mode = 'CALIBRATION'    
                        elif belt_controller.get_belt_mode() == BeltMode.CROSSING:
                            b_mode = 'CROSSING'
                        dt = datetime.datetime.utcnow()
                        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        t_new_now = time.perf_counter_ns()
                        dictionary = {
                            "device": 'BELT',
                            "user_id": beltport_sn,
                            "location": "Dept. of phys. therapy",
                            "pattern": vib_pattern,
                            "intensity": vp3,
                            "orientation_type": "ANGLE",
                            "orientation": BeltHeading_ThreadShared,
                            'frequency': update_freq,
                            "pattern_iterations": vp6,
                            "pattern_start_time": vp8,
                            "timestamp": dt_str,
                            "nansocends of run": t_new_now - t_now_ns,
                            "mode": b_mode,
                            "firmware version": str(belt_controller.get_firmware_version()), 
                            'battery_charge':  100
                        }
                        json_object = json.dumps(dictionary, indent =4)
                        lock.release()

                        outfile.write(json_object)
            print('TOTAL TIME = ', periodsum  / 1000000000)
       # bat_str = belt_controller_delegate.on_belt_battery_notified()
        #bat_str = bat_str.split(" ")
        #battery_lvl = bat_str[2].strip()
        #print(bat_str)

    ########################
    # GET BUTTON PUSHES (vibrate tactor when push pause button)
    ########################
    # note the block of code works. The belt needs to be in app mode so that touching the buttons does not screw with things
    bButtonEventTest = 0
    if bButtonEventTest == 1:
        from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType
        numsecs4test = 5
        t_end = time.time() + numsecs4test
        while time.time() < t_end:
            #time.sleep(1.0)
            #print('one second in loop')
            print('BUTTON', button_pressed_event.is_set())
            if button_pressed_event.is_set() == True:
                from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType
    #            belt_controller.send_vibration_command(
    #                                    channel_index=2,
    #                                    pattern=BeltVibrationPattern.CONTINUOUS,
    #                                    intensity=None, # ranges from 0 to 100
    #                                    orientation_type=BeltOrientationType.ANGLE,
    #                                    orientation=102,
    #                                    pattern_iterations=1,
    #                                    pattern_period=250,  # ms
    #                                    pattern_start_time=0,
    #                                    exclusive_channel=False,
    #                                    clear_other_channels=False)
                from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType, BeltVibrationTimerOption
                belt_controller.send_pulse_command(
                                        channel_index=0,
                                        orientation_type=BeltOrientationType.ANGLE,
                                        orientation=90,
                                        intensity=None,
                                        on_duration_ms=150,
                                        pulse_period=500,
                                        pulse_iterations=3,
                                        series_period=1500,
                                        series_iterations=1,
                                        timer_option=BeltVibrationTimerOption.RESET_TIMER,
                                        exclusive_channel=False,
                                        clear_other_channels=False)
            button_pressed_event.clear()


    ### PYBELT ERROR/DEBUGGING MESSAGES
    ## output debug messages to stdout
    #from functs import belt_controller_log_to_stdout  # (get this function from the functs.py file)
    #belt_controller_log_to_stdout() 


    #############################################
    # TACTOR TEST: VIBRATE EACH TACTOR IN TURN
    #############################################
    bTestTactor_1 = 0
    if bTestTactor_1 == 1:

        from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType
        numTactors = 16
        vp1 = 1 # channel index
        vp2 = BeltVibrationPattern.DOUBLE_LONG # pattern
        vp3 = 50 # intensity
        vp4 = BeltOrientationType.ANGLE # orientation_type (MOTOR_INDEX, ANGLE, ...?)
        vp5 = 0 # orientation,
        vp6 = 1 # pattern_iterations
        vp7 = 250 # pattern_period
        vp8 = 0 # pattern_start_time
        vp9 = False # exclusive_channel
        vp10 = False # clear_other_channels
        
        with open("sample2.json", "w") as outfile:
            for iDegrees in range(0, 360, 3):
                start_time = time.time()
                belt_controller.send_vibration_command(vp1,vp2,vp3,vp4,iDegrees,vp6,vp7,vp8,vp9,vp10)
                print('Tactor # = ',iDegrees)
                if vp2 == 0:
                    vib_pattern = 'NO VIBRATION'
                elif vp2 == 1:
                    vib_pattern = 'CONTINUOUS'
                elif vp2 == 2:
                    vib_pattern == 'SINGLE SHORT'
                elif vp2 == 3:
                    vib_pattern == 'SINGLE_LONG'
                elif vp2 == 4:
                    vib_pattern = 'DOUBLE SHORT'
                else:
                    vib_pattern = 'DOUBLE LONG'
                if belt_controller.get_belt_mode() == BeltMode.STANDBY:
                    b_mode = "STANDBY"
                elif belt_controller.get_belt_mode() == BeltMode.WAIT:
                    b_mode = "WAIT"
                elif belt_controller.get_belt_mode() == BeltMode.COMPASS:
                    b_mode = "COMPASS"
                elif belt_controller.get_belt_mode() == BeltMode.APP_MODE:
                    b_mode = "APP_MODE"
                elif belt_controller.get_belt_mode() == BeltMode.PAUSE:
                    b_mode = "PAUSE"
                elif belt_controller.get_belt_mode() == BeltMode.CALIBRATION:
                    b_mode = 'CALIBRATION'    
                elif belt_controller.get_belt_mode() == BeltMode.CROSSING:
                    b_mode = 'CROSSING'
                dt = datetime.datetime.utcnow()
                dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                dictionary = {
                    "user_id": beltport_sn,
                    "location": "Dept. of phys. therapy",
                    "pattern": vib_pattern,
                    "intensity": vp3,
                    "orientation_type": "ANGLE",
                    "orientation": iDegrees,
                    "pattern_iterations": vp6,
                    "pattern_start_time": vp8,
                    "timestamp": dt_str,
                    "mode": b_mode,
                    "firmware version": str(belt_controller.get_firmware_version()), 
                    'battery_charge':  100
                }
                json_object = json.dumps(dictionary, indent =4)
                outfile.write(json_object)

        print('TACTOR TEST: End')
        
    ##########################################################
    # TACTOR TEST: VIBRATE MULTIPLE TACTORS AT THE SAME TIME
    ##########################################################
    # parameters
    #   angle: Any, 
    #   switch_to_app_mode: bool = True, 
    #   channel_index: int = 1, 
    #   intensity: Any | None = None, 0-100
    #   clear_other_channels: bool = False
    bTestTactor_2 = 0
    if bTestTactor_2 == 1:
        print('### VIBRATE MULTIPLE TACTORS AT THE SAME TIME')
        belt_controller.vibrate_at_angle(102, channel_index=0)
        belt_controller.vibrate_at_angle(124, channel_index=1)
        belt_controller.vibrate_at_angle(147, channel_index=2)
        belt_controller.vibrate_at_angle(169, channel_index=3)
        belt_controller.vibrate_at_angle(192, channel_index=4)
        belt_controller.vibrate_at_angle(214, channel_index=5)
        time.sleep(3.75)
        belt_controller.stop_vibration(None)  # None for all channels

    time.sleep(1.0)

    ##################################################
    # TACTOR TEST: VARY THE INTENSITY OF THE TACTOR
    ##################################################
    # belt_controller.vibrate_at_angle()
    # parameters
    #   angle: Any, 
    #   switch_to_app_mode: bool = True, 
    #   channel_index: int = 1, 
    #   intensity: Any | None = None, 0-100
    #   clear_other_channels: bool = False
    bTestTactor_3 = 0
    if bTestTactor_3 == 1:
        # ramp up the intensity of vibration
        for iIntensity in range(0, 100, 1):
            belt_controller.vibrate_at_angle(124, channel_index=1,intensity=iIntensity)
            print('Intensity # = ',iIntensity)
            time.sleep(0.1)
        # stop the vibration
        belt_controller.stop_vibration(None)  # None for all channels

    ########################################################
    # TACTOR TEST: send more specific commands to the belt
    ########################################################
    bTestTactor_4 = 0
    if bTestTactor_4 == 1:
        from pybelt.belt_controller import BeltVibrationPattern, BeltOrientationType
        print('### SENDING VIBRATION COMMAND')
        belt_controller.send_vibration_command(
                            channel_index=2,
                            pattern=BeltVibrationPattern.CONTINUOUS,
                            intensity=None, # ranges from 0 to 100
                            orientation_type=BeltOrientationType.ANGLE,
                            orientation=0,
                            pattern_iterations=1,
                            pattern_period=3000,
                            pattern_start_time=0,
                            exclusive_channel=False,
                            clear_other_channels=False)
        time.sleep(5.75)
        belt_controller.stop_vibration()
        

    time.sleep(0.75)

    #########################
    # DISCONNECT FROM BELT
    #########################
    belt_controller.set_orientation_notifications(False)
    belt_controller.disconnect_belt()
    print('Connection State = ', belt_controller.get_connection_state())




    print('end')

####################################
# Python Interpreter Entry Point
####################################
# only run code inside this if-statement if this .py file is being run directly by the python interpreter 
if __name__ == "__main__":  
    print('Starting main process')
    main()
    print('Ending main process')
