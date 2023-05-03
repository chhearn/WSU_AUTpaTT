#------------------------------------------------------------------------------
#'MotorController.py'                               Hearn WSU-ECE
#                                                   17apr23
# Open-Source Antenna Pattern Measurement System
# Performs the following motor-controller interface & commands:
#  1. _init_
#  2. connect 
#  3. disconnect
#  4. is_connected 
#  5. get_controller_angles
#  6. get_current_angles
#  7. send_movement_command
#  8. rotate_mast
#  9. rotate_arm
# 10. reset_angles
# 11. send_homing_command
# 12. reset_orientation
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# WSU legal statement here
#------------------------------------------------------------------------------
import serial
import time
#                                                           
class MotorController():
    def __init__(self, serial_device, baudrate):
        self.serial_device = serial_device
        self.serial_baudrate = baudrate
        self.connection = None
        self.mast_angle = 0.0
        self.arm_angle = 0.0
    #--------------------------------------------------------------------------
    #
    #--------------------------------------------------------------------------
    def connect(self):
        self.connection = serial.Serial()
        self.connection.port = self.serial_device
        self.connection.baudrate = self.serial_baudrate
        self.connection.timeout = 1
        self.connection.dtr = 0                              # don't reset ucntrllr 
        try:                                                 # when connecting
            self.connection.open()
        except Exception as e:
            print("Failed to connect to motor controller on {:s}\nCheck the port settings\n".format(self.connection.port),e)
            # print("Failed to connect to motor controller on {:s}\n")
            #print("Check port settings\n".format(self.connection.port),e)
            raise e
        connect_msg = ""
        connect_tries = 10
        while connect_msg.strip() == "" and connect_tries > 0:
            connect_msg = self.connection.readline().decode('ascii')
            connect_tries = connect_tries - 1 
        print("Connect response: ", connect_msg)
        self.connection.write(("G1 F500\n").encode())         # 500 units/s max
        response = self.connection.readline().decode('ascii')
        print("Set feedrate response: ", response)
        if connect_msg.find("Grbl 1.1f") < 0 or connect_tries == 0 or response[:2] != "ok":
            self.connection = None
            return False
        else:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            return True
    def disconnect(self):
        self.connection.close()
        self.connection = None
    def is_connected(self):
        if self.connection is not None:
            return self.connection.is_open
        else:
            return False
    #--------------------------------------------------------------------------
    # get the current angles (position) from the controller firmware
    # find the MPos data segment
    # extract angles from the data segment "MPos:x,y,z"
    #--------------------------------------------------------------------------
    def _get_controller_angles(self):
        self.connection.write(("?").encode())
        response = self.connection.readline().decode('ascii')
        mpos = ""
        found = False
        for part in response.split("|"):
            if part.find("MPos") == 0:
                mpos = part
                found = True
        if found:
            mast_angle = mpos.split(":")[1].split(",")[0]
            arm_angle = mpos.split(":")[1].split(",")[1]
            return (mast_angle, arm_angle)
        else:
            return None
    #
    def get_current_angles(self):
        return (self.mast_angle, self.arm_angle)
    #--------------------------------------------------------------------------
    # send actual movement command
    # send "wait for last movement to complete" command
    #--------------------------------------------------------------------------
    def _send_movement_command(self, axis, amount):
        xtest = "G1 "+str(axis)+str(amount)+"\n"
        self.connection.write(xtest.encode())
        print("The amount is ", amount)
        print("The Axis is' ", axis)
        response1 = self.connection.readline().decode('ascii')
        print("Move response: ", response1)
        if response1[:5] == "error":
            return False
        self.connection.write(("G4 P0\n").encode())
        timeout = 30                                                 # seconds
        start_time = time.process_time()
        stop_time = start_time
        while (stop_time - start_time) < timeout:
            response2 = self.connection.readline().decode('ascii')
            print("Wait response: ", response2)
            if response2[:5] == "error":
                return False
            elif response2[:2] == "ok":
                return True                                          # Timedout
        return False
    #--------------------------------------------------------------------------
    # rotate the mast (upright portion) by the given number of degrees,
    # X axis, positive values for CW, negative for CCW 
    # (as seen when looking from top of mast downwards)
    #--------------------------------------------------------------------------
    def rotate_mast(self, degrees):
        amount = degrees
        if self._send_movement_command("X", amount):
            self.mast_angle += degrees
            return True
        else:
            return False
    #--------------------------------------------------------------------------
    # rotate the arm (lengthwise portion)  by the given number of degrees,
    # Y axis, positive values for CW, negative for CCW 
    # (as seen when looking from outer end of arm towards mast)
    #--------------------------------------------------------------------------
    def rotate_arm(self, degrees):
        amount = degrees
        if self._send_movement_command("Y", amount):
            self.arm_angle += degrees
            return True
        else:
            return False
    #--------------------------------------------------------------------------
    # reset the controller angles (position)
    #--------------------------------------------------------------------------
    def _reset_angles(self):
        self.connection.write(("G92.1\n").encode())
        response = self.connection.read(4)
        if response != "ok\r\n":
            return False
        else:
            #------------------------------------------------------------------
            # reset internal angles
            #------------------------------------------------------------------
            self.mast_angle = 0.0
            self.arm_angle = 0.0
            return True
    #--------------------------------------------------------------------------
    # TODO remove when homing sensors installed
    # send the homing command to the controller
    #--------------------------------------------------------------------------
    def _send_homing_command(self):
        return True 
        self.connection.write(("$H\n").encode())
        response = self.connection.read(4)
        if response != "ok\r\n":
            return False
        else:
            return True
    def reset_orientation(self):
        return self._send_homing_command() and self._reset_angles()


