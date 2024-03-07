# TO DO
# threaded version
# - pass pptnum of filename into function
# - need to coordinate times of system and MTi ... see my C++ code
# make sure return magNorm for quality check
# Decode log file ... see if contents of log file depend upon the code


# XSENS SETUP
# _LAB MANUAL_Mti 630 DK.docx
# make sure you have used the Magnetivc Field Mapper to get a good calibration (want calibration to give a NormMag value close to 1 with minimal variability)
#     - at end of mapping make sure to press write to device
# make sure you have local GPS coordinates uploaded into the hardware
#     - setting including local GPS are in CONFIG-MTi 600_WithCTGPSLocale2.xsa
# magnorm
#       https://base.xsens.com/s/article/Calculating-the-Magnetic-Norm-Mag-Norm?language=en_US

# VS CODE SETUP
# python -m venv ve_xsens
# SELECT THE venv interpreter through command pallete
# ve_xsens\Scripts\activate
# pip install xsensdeviceapi-2022.0.0-cp39-none-win_amd64.whl #this file must be local

# this code in the python example code from xsens. (see example_mti_receive_data.py)
#   - connects the the xsens 
#   - displays data to the console for 20 seconds
#   - create a log file that is has an IMU time code

import sys
import xsensdeviceapi as xda
from threading import Lock
import math
from test_client import Client
import time

class XdaCallback(xda.XsCallback):
    def __init__(self, max_buffer_size = 5):
        xda.XsCallback.__init__(self)
        self.m_maxNumberOfPacketsInBuffer = max_buffer_size
        self.m_packetBuffer = list()
        self.m_lock = Lock()

    def packetAvailable(self):
        self.m_lock.acquire()
        res = len(self.m_packetBuffer) > 0
        self.m_lock.release()
        return res

    def getNextPacket(self):
        self.m_lock.acquire()
        assert(len(self.m_packetBuffer) > 0)
        oldest_packet = xda.XsDataPacket(self.m_packetBuffer.pop(0))
        self.m_lock.release()
        return oldest_packet

    def onLiveDataAvailable(self, dev, packet):
        self.m_lock.acquire()
        assert(packet is not 0)
        while len(self.m_packetBuffer) >= self.m_maxNumberOfPacketsInBuffer:
            self.m_packetBuffer.pop()
        self.m_packetBuffer.append(xda.XsDataPacket(packet))
        self.m_lock.release()


print('MTi630: We are running OK')


if __name__ == '__main__':
    
    print("MTi630: Creating XsControl object...")
    control = xda.XsControl_construct()
    assert(control is not 0)

    xdaVersion = xda.XsVersion()
    xda.xdaVersion(xdaVersion)
    print("MTi630: Using XDA version %s" % xdaVersion.toXsString())
    
    MagNorm = 0

    try:
        print("MTi630: Scanning for devices...")
        portInfoArray =  xda.XsScanner_scanPorts()
        # Find an MTi device
        mtPort = xda.XsPortInfo()
        for i in range(portInfoArray.size()):
            if portInfoArray[i].deviceId().isMti() or portInfoArray[i].deviceId().isMtig():
                mtPort = portInfoArray[i]
                break

        if mtPort.empty():
            raise RuntimeError("No MTi device found. Aborting.")

        did = mtPort.deviceId()
        print("MTi630: Found a device with:")
        print("        Device ID: %s" % did.toXsString())
        print("        Port name: %s" % mtPort.portName())

        print("MTi630: Opening port...")
        if not control.openPort(mtPort.portName(), mtPort.baudrate()):
            raise RuntimeError("Could not open port. Aborting.")

        print("MTi630: BAUDRATE:    ",mtPort.baudrate())
        
        # Get the device object
        device = control.device(did)
        assert(device is not 0)

        print("MTi630: Device: %s, with ID: %s opened." % (device.productCode(), device.deviceId().toXsString()))

        # Create and attach callback handler to device
        callback = XdaCallback()
        device.addCallbackHandler(callback)
        

        ##########################################
        # DEVICE SETTINGS
        ##########################################
        # Note: If want to set as DEFAULT (i.e. what is already on the device use 0 as second parameter in XsOutputConfiguration function)

        # Put the device into CONFIGURATION MODE before configuring the device
        print("MTi630: Putting device into configuration mode...")
        if not device.gotoConfig():
            raise RuntimeError("Could not put device into configuration mode. Aborting.")

        print("MTi630: Configuring the device...")
        configArray = xda.XsOutputConfigurationArray()

        if device.deviceId().isVru() or device.deviceId().isAhrs():
            print('MTi630: I am talking to an AHRS device')  # isAhrs() IS THE MTi-630 SENSOR 
        else:
            raise RuntimeError("MTi630: Unknown device while configuring. Aborting.")
        

        # NEED TO CHECK THAT HAVE CORRECT FILTER - NOT SURE HOW TO DO THIS YET 
        # Not sure how to set filters in the code ... see fist try below
        #xdaFilterProfile = xda.XsFilterProfile()
        #xda.xdaFilterProfile(xdaFilterProfile)
        #print("MTi630: xdaFilterProfile %s" % xdaFilterProfile.toXsString())
        
        ##setXdaFilterProfile
        ##device.setOnboardFilterProfile("Robust/VRU")
        ##xdaVersion = xda.XsVersion()
        ##xda.xdaVersion(xdaVersion)
        ##print("MTi630: Using XDA version %s" % xdaVersion.toXsString())

        # SET ORIENTATION COORDINATE SYSTEM (this causes a crash at the moment)
        #configArray.push_back(xda.XsOutputConfiguration(xda.XDI_CoordSysEnu, 0)); # XDI_CoordSysEnu   XDI_CoordSysNed   XDI_CoordSysNwu

        # SET THE DATA TO BE PACKAGED AND SENT FROM THE DEVICE
        # Baudrate
        MTi630_Settings_baudRate = 460800                                       # may want to use 2000000 if have any "fine grained measures"
        # Data Packet Count                                 <--YES
        MTi630_Settings_DataPacketCount_bActive = True                          # index of data packets (this is used by this code so it is not an option to not have it)(it is also used in matlab for error checking)
        MTi630_Settings_DataPacketCount_SampleRate = 0		                    # set this as default (default setting is requested via value of 0)
        # Rate of Turn                                      <--YES
        MTi630_Settings_RateOfTurn_bActive = True
        MTi630_Settings_RateOfTurn_SampleRate = 100			                    # 400 is the max (Run MT Manager to see possible settings)
        # Time (Fine Grained)
        MTi630_Settings_HardwareTime_FineGrained_bActive = True
        MTi630_Settings_HardwareTime_FineGrained_SampleRate = 0                 # set this as default (default setting is requested via value of 0)
        # Orientation (quaternion)                          <--YES
        MTi630_Settings_Orientation_Quaternion_bActive = True
        MTi630_Settings_Orientation_Quaternion_SampleRate = 100                 # 400 is the max (Run MT Manager to see possible settings)
        # Orientation (Euler)                          <--YES
        MTi630_Settings_Orientation_Euler_bActive = True
        MTi630_Settings_Orientation_Euler_SampleRate = 100                      # 400 is the max (Run MT Manager to see possible settings)
        # Orientation (Matrix)
        MTi630_Settings_Orientation_Matrix_bActive = False
        MTi630_Settings_Orientation_Matrix_SampleRate = 100                      # 400 is the max (Run MT Manager to see possible settings)
        # Acceleration                                      <--YES
        MTi630_Settings_Acceleration_bActive = True                             # Acceleration output in m/s2.
        MTi630_Settings_Acceleration_SampleRate = 100                           # 400 is the max (Run MT Manager to see possible settings)
        # Magnetic Field (Calibrated)                                   <--YES
        MTi630_Settings_MagneticField_bActive = True
        MTi630_Settings_MagneticField_SampleRate = 100			                # 100 is the max (Run MT Manager to see possible settings)
        # Acceleration (Free Accleration)
        MTi630_Settings_Acceleration_Free_bActive = False
        MTi630_Settings_Acceleration_Free_SampleRate = 0			            # 400 is the max (Run MT Manager to see possible settings)
        # Acceleration (HIGH RESOLUTION)
        MTi630_Settings_Acceleration_HR_bActive = False
        MTi630_Settings_Acceleration_HR_SampleRate = 1000	                    # 2000 is the max (Run MT Manager to see possible settings)
        # Rate of Turn (HIGH RESOLUTION)
        MTi630_Settings_RateOfTurn_HR_bActive = False
        MTi630_Settings_RateOfTurn_HR_SampleRate = 1000	                        # 2000 is the max (Run MT Manager to see possible settings)
        # Temperature (not sure this works all that well)
        MTi630_Settings_Temperature_bActive = False
        MTi630_Settings_Temperature_SampleRate = 100			                # 400 is the max (Run MT Manager to see possible settings)
        
        # DO NOT SEEM TO BE ABLE TO GET PACKETS FOR THE FOLLOWING (LEAVE AS FALSE)
        # Barometer
        MTi630_Settings_BaroPressure_bActive = False
        MTi630_Settings_BaroPressure_SampleRate = 100			                # 100 is the max (Run MT Manager to see possible settings)
        # Triggers
        MTi630_Settings_TriggerIn1_bActive = False
        MTi630_Settings_TriggerIn1_SampleRate = 0		                        # set this as default (default setting is requested via value of 0)
        MTi630_Settings_TriggerIn2_bActive = False
        MTi630_Settings_TriggerIn2_SampleRate = 0		                        # set this as default (default setting is requested via value of 0)
        # Magnetic Field (Raw and Converted to Floats)                                   <--YES
        MTi630_Settings_MagneticFieldRaw_bActive = False
        MTi630_Settings_MagneticFieldRaw_SampleRate = 100			                # 100 is the max (Run MT Manager to see possible settings)
        # Magnetic Field (Corrected)                        <-NOT SURE WHAT THIS IS NEED TO FIND OUT WHAT THIS IS
        MTi630_Settings_MagneticFieldCorrected_bActive = False                   # Corrected Magnetic field data in a.u. (ICC result)
        MTi630_Settings_MagneticFieldCorrected_SampleRate = 100			        # 100 is the max (Run MT Manager to see possible settings)
        # Time UTC                                          <--YES
        MTi630_Settings_HardwareTime_UTC_bActive = False
        MTi630_Settings_HardwareTime_UTC_SampleRate = 100       
        # Velocity
        MTi630_Settings_Velocity_bActive = True
        MTi630_Settings_Velocity_SampleRate = 100

        #########################################################
        # Use parameters just set to build a configArray
        #########################################################
        # PACKET INDEX: index of data packets (this is used by this code so it is not an option to not have it)(it is also used in matlab for error checking)
        if MTi630_Settings_DataPacketCount_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_PacketCounter, MTi630_Settings_DataPacketCount_SampleRate)) 
        # Time (Fine Grained)
        if MTi630_Settings_HardwareTime_FineGrained_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_SampleTimeFine, MTi630_Settings_HardwareTime_FineGrained_SampleRate))
        # Orientation (Quaternion)
        if MTi630_Settings_Orientation_Quaternion_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, MTi630_Settings_Orientation_Quaternion_SampleRate))
        # Orientation (Euler)
        if MTi630_Settings_Orientation_Euler_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_EulerAngles, MTi630_Settings_Orientation_Euler_SampleRate))
        # Orientation (Matrix)
        if MTi630_Settings_Orientation_Matrix_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RotationMatrix, MTi630_Settings_Orientation_Matrix_SampleRate))
        # Acceleration    
        if MTi630_Settings_Acceleration_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, MTi630_Settings_Acceleration_SampleRate))
        # Magnetic Field   
        if MTi630_Settings_MagneticField_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, MTi630_Settings_MagneticField_SampleRate))
        # Acceleration (Free Accleration)
        if MTi630_Settings_Acceleration_Free_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_FreeAcceleration, MTi630_Settings_Acceleration_Free_SampleRate))
        # Acceleration (HIGH RESOLUTION)
        if MTi630_Settings_Acceleration_HR_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_AccelerationHR, MTi630_Settings_Acceleration_HR_SampleRate))
        # Rate of Turn       
        if MTi630_Settings_RateOfTurn_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, MTi630_Settings_RateOfTurn_SampleRate))
        # Rate of Turn (HIGH RESOLUTION)  
        if MTi630_Settings_RateOfTurn_HR_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurnHR, MTi630_Settings_RateOfTurn_HR_SampleRate))
        # Temperature       
        if MTi630_Settings_Temperature_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Temperature, MTi630_Settings_Temperature_SampleRate))
        
        #####################THESE VARIABLES DON'T SEEEM TO CREATE PACKETS WHEN PUSH THEM
        # UTC TIME STAMPS
        if MTi630_Settings_HardwareTime_UTC_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_UtcTime, MTi630_Settings_HardwareTime_UTC_SampleRate))
        # Baro Pressure       
        if MTi630_Settings_BaroPressure_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_BaroPressure, MTi630_Settings_BaroPressure_SampleRate))
        # Trigger 1
        if MTi630_Settings_TriggerIn1_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_TriggerIn1, MTi630_Settings_TriggerIn1_bActive))
        # Trigger 2
        if MTi630_Settings_TriggerIn2_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_TriggerIn2, MTi630_Settings_TriggerIn2_bActive))
        # Velocity       
        if MTi630_Settings_Velocity_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_VelocityXYZ, MTi630_Settings_Velocity_SampleRate))
        # Magnetic Field (Raw)
        if MTi630_Settings_MagneticFieldRaw_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RawMag, MTi630_Settings_MagneticFieldRaw_SampleRate))
        # Magnetic Field (Corrected)
        if MTi630_Settings_MagneticFieldCorrected_bActive == True:
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticFieldCorrected, MTi630_Settings_MagneticFieldCorrected_SampleRate))

        ##########################################
        # SET THE CONFIG ON THE DEVICE
        ##########################################
        if not device.setOutputConfiguration(configArray):
            raise RuntimeError("MTi630: Could not configure the device. Aborting.")

        #############################################
        # CREATE A LOG FILE
        #############################################
        print("MTi630: Creating a log file...")
        logFileName = "logfile.mtb"
        if device.createLogFile(logFileName) != xda.XRV_OK:
            raise RuntimeError("MTi630: Failed to create a log file. Aborting.")
        else:
            print("MTi630: Created a log file: %s" % logFileName)

        # Put the device back into MEASUREMENT MODE before starting data collection
        print("MTi630: Putting device into measurement mode...")
        if not device.gotoMeasurement():
            raise RuntimeError("Could not put device into measurement mode. Aborting.")

        print("MTi630: Starting recording...")
        if not device.startRecording():
            raise RuntimeError("Failed to start recording. Aborting.")

        ######################################################
        # Connecting to Socket Server
        ######################################################

        client = Client('127.0.0.1', 12345)
        client.connect('imu', 's', 'belt')

######## ZMQ

        # import zmq

        # context = zmq.Context()

        # #  Socket to talk to server
        # socket = context.socket(zmq.REQ)
        # socket.connect("tcp://localhost:5555")

        ################################
        # START DATA COLLECTION
        ################################

        startTime = xda.XsTimeStamp_nowMs() # this gets the time stamp in the hardware (Can compare this to system time)

        print('startTime is a :',type(startTime), ' = ', startTime)

        print("Main loop. Recording data for 10 seconds.")
        count = 1
        while xda.XsTimeStamp_nowMs() - startTime <= 60000:
            if callback.packetAvailable():
                # Retrieve a packet
                packet = callback.getNextPacket()

                # initialize string for 
                s = ""

                if packet.containsOrientation() == True:
                    quaternion = packet.orientationQuaternion() # quaternion[0] quaternion[1] quaternion[2] quaternion[3] (q1 q2 q3 q4)
                    euler = packet.orientationEuler() # euler.x() euler.y() euler.z()
                    bPrint_orientationQuaternion = False
                    if bPrint_orientationQuaternion == True:
                        s +=  "| q0: %5.2f" % quaternion[0] + ", q1: %5.2f" % quaternion[1] + ", q2: %5.2f" % quaternion[2] + ", q3: %5.2f " % quaternion[3]
                    bPrint_orientationEuler = True
                    if bPrint_orientationEuler == True:
                        # s += " | Roll: %5.2f" % euler.x() + ", Pitch: %5.2f" % euler.y() + ", Yaw: %5.2f " % euler.z()
                        s += "%5.2f" % euler.z()
                
                # if packet.containsCalibratedGyroscopeData():  # WARNING GETTING GYRO DATA ONLY WORKS WHEN HAVE RATE OF TURN PACKET 
                #     gyr = packet.calibratedGyroscopeData() # gyr[0] gyr[1] gyr[2] (X Y Z)
                #     bPrint_Gyroscope = False
                #     if bPrint_Gyroscope == True:
                #         s += " | GX: %5.2f" % gyr[0] + ", GY: %5.2f" % gyr[1] + ", GZ: %5.2f" % gyr[2]
                    
                # if packet.containsCalibratedAcceleration() == True:
                #     acc = packet.calibratedAcceleration()  # acc[0] acc[1] acc[2] (X Y Z)
                #     bPrint_CalibratedAcceleration = False
                #     if bPrint_CalibratedAcceleration == True:
                #         s += " | AX: %5.2f" % acc[0] + ", AY: %5.2f" % acc[1] + ", AZ: %5.2f" % acc[2]
                #     #--> update thread shared variables

                # if packet.containsCalibratedMagneticField() == True:
                #     mag = packet.calibratedMagneticField() # magCal[0] magCal[0] magCal[0] (X Y Z)
                #     # calculate mag norm
                #     #     https://base.xsens.com/s/article/Calculating-the-Magnetic-Norm-Mag-Norm?language=en_US
                #     MagNorm = math.sqrt(pow(abs(mag[0]),2) + pow(abs(mag[1]),2) + pow(abs(mag[2]),2))
                #     #--> update thread shared variables
                #     bPrint_calibratedMagneticField = True
                #     if bPrint_calibratedMagneticField == True:
                #         s += "   "
                #         s += " | Mag(Cal) X: %5.2f" % mag[0] + ", MY: %5.2f" % mag[1] + ", MZ: %5.2f" % mag[2] + ", MagNorm: %5.2f" % MagNorm
                   
                # # can get this data
                # if packet.containsFreeAcceleration() == True:
                #     accFree = packet.freeAcceleration()  # acc[0] acc[1] acc[2] (X Y Z) (m/s^2)
                #     bPrint_FreeAcceleration = False
                #     if bPrint_FreeAcceleration == True:
                #         s += " | AX: %5.2f" % accFree[0] + ", AY: %5.2f" % accFree[1] + ", AZ: %5.2f" % accFree[2]

                # if packet.containsAccelerationHR() == True:
                #     accHR = packet.accelerationHR()  # acc[0] acc[1] acc[2] (X Y Z) (m/s^2)
                #     bPrint_Acceleration_HR = False
                #     if bPrint_Acceleration_HR == True:
                #         s += " | AX: %5.2f" % accHR[0] + ", AY: %5.2f" % accHR[1] + ", AZ: %5.2f" % accHR[2] 

                # if packet.containsRateOfTurnHR() == True:
                #     rateOfTurnHR = packet.rateOfTurnHR()  # rateOfTurn[0] rateOfTurn[1] rateOfTurn[2] (X Y Z) (m/s)
                #     bPrint_RateOfTurnHR = False
                #     if bPrint_RateOfTurnHR == True:
                #         s += " | AX: %5.2f" % rateOfTurnHR[0] + ", AY: %5.2f" % rateOfTurnHR[1] + ", AZ: %5.2f" % rateOfTurnHR[2] 

                # if packet.containsTemperature():
                #     #print('TEMPERATURE PACKET PRESENT!')
                #     temp = packet.temperature()  # float
                #     #print(type(temp))
                #     Print_containsTemperature = False
                #     if Print_containsTemperature == True:
                #         s += " |Temp: %7.2f" % temp
                #     #--> update thread shared variables


                

                # # DO NOT SEEM TO BE ABLE TO GET THIS PACKET
                # if packet.containsRawMagneticField() == True:
                #     print('RAW MAG FIELD PACKET PRESENT!')
                #     #magRaw = packet.rawMagneticFieldConverted() # magRaw[0] magRaw[0] magRaw[0] (X Y Z) (converted to float)
                #     magRaw = packet.rawMagneticField() # magRaw[0] magRaw[0] magRaw[0] (X Y Z)
                #     Print_RawMagneticField = False
                #     if Print_RawMagneticField == True:
                #         s += " | Mag(Rawe) X: %5.2f" % magRaw[0] + ", MY: %5.2f" % magRaw[1] + ", MZ: %5.2f" % magRaw[2]
                #     #--> update thread shared variables

                # # DO NOT SEEM TO BE ABLE TO GET THIS PACKET
                # if packet.containsCorrectedMagneticField() == True:
                #     print('CORRECTED MAG FIELD PACKET PRESENT!')
                #     magCor = packet.correctedMagneticField() # magCor[0] magCor[0] magCor[0] (X Y Z)
                #     print(type(magCor))
                #     bPrint_CorrectedMagneticField = True
                #     if bPrint_CorrectedMagneticField == True:
                #         s += " | Mag(Cor) X: %5.2f" % magCor[0] + ", MY: %5.2f" % magCor[1] + ", MZ: %5.2f" % magCor[2]
                #     #--> update thread shared variables

                # # DO NOT SEEM TO BE ABLE TO GET THIS PACKET
                # if packet.containsVelocity():
                #     print('VELOCITY PACKET PRESENT!')
                #     vel = packet.velocity(xda.XDI_CoordSysEnu) # vel[0] vel[1] vel[2] (E N U)
                #     Print_Velocity = False
                #     if Print_Velocity == True:
                #         s += " |E: %7.2f" % vel[0] + ", N: %7.2f" % vel[1] + ", U: %7.2f " % vel[2]
                #     #--> update thread shared variables

                # data = {
                #     'heading': s,
                #     'size': len(b'{s}')
                # }
                
                # if count == 1:
                #     start = time.time()

                # count +=1 
                # tims = time.time() - start + 0.0000000001
                # print(f"{round(count/(tims), 8)}, {count}, {tims}\r", end='', flush=True)
                # # print(s)
                # socket.send(f"{s}".encode())
                
                # message = socket.recv()
                print(s)
                client.send_data_stream(data=s)
                # client.data=s
                # client.listen_to_server()
                #print("%s\r" % s, end="", flush=True)
                # print(f"{s}\r", end="", flush=True)
                #print("%s\r" % s2, end="", flush=True)
                #print("%f\r" % euler.z(), end="", flush=True)
                


        print("\nStopping recording...")
        if not device.stopRecording():
            raise RuntimeError("Failed to stop recording. Aborting.")

        print("Closing log file...")
        if not device.closeLogFile():
            raise RuntimeError("Failed to close log file. Aborting.")

        print("Removing callback handler...")
        device.removeCallbackHandler(callback)

        print("Closing port...")
        control.closePort(mtPort.portName())

        print("Closing XsControl object...")
        control.close()

    except RuntimeError as error:
        print(error)
        sys.exit(1)
    except:
        print("An unknown fatal error has occured. Aborting.")
        sys.exit(1)
    else:
        print("Successful exit.")






        '''

         if device.deviceId().isVru() or device.deviceId().isAhrs():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, 100))
        else:
            raise RuntimeError("Unknown device while configuring. Aborting.")
        if not device.setOutputConfiguration(configArray):
            raise RuntimeError("Could not configure the device. Aborting.")


        if device.deviceId().isImu():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, 100))
            print("Device ID = IMU")
        elif device.deviceId().isVru() or device.deviceId().isAhrs():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, 100))

            print("Device ID = AHRS or VRU")
        elif device.deviceId().isGnss():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_LatLon, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_AltitudeEllipsoid, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_VelocityXYZ, 100))
            print("Device ID = GNSS")
        else:
            raise RuntimeError("Unknown device while configuring. Aborting.")



               s = ""

                # The packet.containsCalibratedData() function only returns true when a data packet contains 
                # all three sensor data components: CalibratedAcceleration, CalibratedGyroscopeData and CalibratedMagneticField.
                if packet.containsCalibratedData():
                    acc = packet.calibratedAcceleration()
                    #s = "AX: %.2f" % acc[0] + ", AY: %.2f" % acc[1] + ", AZ: %.2f" % acc[2]
                    s = "AX: %5.2f" % acc[0] + ", AY: %5.2f" % acc[1] + ", AZ: %5.2f" % acc[2]

                    gyr = packet.calibratedGyroscopeData()
                    #s += " |GX: %.2f" % gyr[0] + ", GY: %.2f" % gyr[1] + ", GZ: %.2f" % gyr[2]
                    s += " |GX: %5.2f" % gyr[0] + ", GY: %5.2f" % gyr[1] + ", GZ: %5.2f" % gyr[2]
                    
                    mag = packet.calibratedMagneticField()
                    #s += " | MX: %.2f" % mag[0] + ", MY: %.2f" % mag[1] + ", MZ: %.2f" % mag[2]
                    s += " | MX: %5.2f" % mag[0] + ", MY: %5.2f" % mag[1] + ", MZ: %5.2f" % mag[2]

                    # calculate mag norm
                    # https://base.xsens.com/s/article/Calculating-the-Magnetic-Norm-Mag-Norm?language=en_US
                    MagNorm = math.sqrt(pow(abs(mag[0]),2) + pow(abs(mag[1]),2) + pow(abs(mag[2]),2))

                    s += " | M(Norm): %5.2f" % MagNorm



                if packet.containsOrientation():
                    quaternion = packet.orientationQuaternion()
                    s +=  "q0: %5.2f" % quaternion[0] + ", q1: %5.2f" % quaternion[1] + ", q2: %5.2f" % quaternion[2] + ", q3: %5.2f " % quaternion[3]
                    euler = packet.orientationEuler()
                    s += " | Roll: %5.2f" % euler.x() + ", Pitch: %5.2f" % euler.y() + ", Yaw: %5.2f " % euler.z()


                #if packet.containsOrientation():
                    
                    #quaternion = packet.orientationQuaternion()
                    #s = "q0: %.2f" % quaternion[0] + ", q1: %.2f" % quaternion[1] + ", q2: %.2f" % quaternion[2] + ", q3: %.2f " % quaternion[3]
                    #s = "q0: %5.2f" % quaternion[0] + ", q1: %5.2f" % quaternion[1] + ", q2: %5.2f" % quaternion[2] + ", q3: %5.2f " % quaternion[3]

                    #euler = packet.orientationEuler()
                    #s += " | Roll: %.2f" % euler.x() + ", Pitch: %.2f" % euler.y() + ", Yaw: %.2f " % euler.z()
                    #s += " | Roll: %5.2f" % euler.x() + ", Pitch: %5.2f" % euler.y() + ", Yaw: %5.2f " % euler.z()


                if packet.containsLatitudeLongitude():
                    latlon = packet.latitudeLongitude()
                    s += " |Lat: %7.2f" % latlon[0] + ", Lon: %7.2f " % latlon[1]

                if packet.containsAltitude():
                    s += " |Alt: %7.2f " % packet.altitude()

                if packet.containsVelocity():
                    vel = packet.velocity(xda.XDI_CoordSysEnu)
                    s += " |E: %7.2f" % vel[0] + ", N: %7.2f" % vel[1] + ", U: %7.2f " % vel[2]

                
                
 print("%s\r" % s, end="", flush=True)
        '''

        
