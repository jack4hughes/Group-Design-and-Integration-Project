from Robot import Robot
from Joint import PrismaticJoint, RevoluteJoint
from inputs import devices
import hid
import os
import time
from typing import List
from pprint import pprint
from collections import deque
import numpy as np
from datetime import datetime

DEFAULT_JOYSTICK_VALUE = 32768
MAX_JOYSTICK_VALUE = 65536
MAX_TRIGGER_VALUE = 1024
DEADSPOT_SIZE = 2500

def find_xbox_controller():
    list_of_hid_devices = hid.enumerate()
    list_of_xbox_controllers = [item for item in list_of_hid_devices if 'Xbox Wireless Controller' in item['product_string']]
    first_xbox_controller_found = list_of_xbox_controllers[0]

    xbox_controller_info = (first_xbox_controller_found['vendor_id'], first_xbox_controller_found['product_id'])
    return xbox_controller_info


class CircularBuffer:
    """A simple class that creates a circular buffer. This records the last x values of an input."""
    def __init__(self, buffer_size = None, initial_values = None):
        if buffer_size == None:
            buffer_size == len(initial_values)

        if initial_values == None:
            intial_values = np.zeros(buffer_size)
        
        self.__current_position = 0
        self.values = initial_values
        self.buffer_size = buffer_size


    def append(self, value):
        self.values[self.__current_position] = value
        self.__current_position += 1


    def mean(self):
        return np.mean(self.values)

    

def create_joystick_buffer_dict(buffer_size):
    initial_buffer_values = CircularBuffer(buffer_size) #our intial robot speed will always be 0 so we can do this.

    buffer_dict = {"vertical": CircularBuffer(buffer_size),
                   "horizontal": CircularBuffer(buffer_size)
                   }
    
    return buffer_dict


def create_trigger_buffer_dict(buffer_size):
    initial_buffer_values = deque([0 for x in range(buffer_size)], maxlen=buffer_size) #our intial robot speed will always be 0 so we can do this.

    buffer_dict = {"left": initial_buffer_values.copy(),
                   "right": initial_buffer_values.copy()
                   }
    
    return buffer_dict


class RobotController:
    def __init__(self, robot: Robot):
        self.robot = robot


class XBoxController:
    def __init__(self, 
                 robot: Robot, 
                 start_bin = 1118, 
                 end_bin = 2835,
                 buffer_length = 100):
        
        super().__init__()
        self.hid_input = hid.device()
    
        try:
            self.hid_input.open(start_bin, end_bin)
            self.hid_input.set_nonblocking(True)
        except:
            print("HID Controller couldn't be opened! Please check this list of avaiable HID inputs")
        # Setting default values for each control.
        
        self.left_joystick_raw_values = {"x": DEFAULT_JOYSTICK_VALUE, "y": DEFAULT_JOYSTICK_VALUE} #sets up dict
        self.right_joystick_raw_values = {"x": DEFAULT_JOYSTICK_VALUE, "y": DEFAULT_JOYSTICK_VALUE}

        #self.left_joystick_buffer = create_trigger_buffer_dict(self.left_joystick_raw_values)
        #self.left_joystick_buffer = create_trigger_buffer_dict(self.left_joystick_raw_values)

        self.left_trigger = 0
        self.right_trigger = 0

        self.a_button = False
        self.b_button = False
        self.x_button = False
        self.y_button = False

        self.left_bumper = 0
        self.right_bumper = 0

        self.deadspot_min = DEFAULT_JOYSTICK_VALUE - DEADSPOT_SIZE
        self.deadspot_max = DEFAULT_JOYSTICK_VALUE + DEADSPOT_SIZE

        self.last_report = None



    def poll_controller(self): 
        """updates controller inputs if controller is found."""
        report = self.hid_input.read(64) #reads relevant bytes
        if len(report) > 10:
            self.left_joystick_raw_values["x"] = report[2] << 8 | report[1]
            self.left_joystick_raw_values["y"] = report[4] << 8 | report[3]

            self.right_joystick_raw_values["x"] = report[6] << 8 | report[5]
            self.right_joystick_raw_values["y"] = report[8] << 8 | report[7]

            self.left_trigger = report[10] << 8 | report[9]
            self.right_trigger = report[12] << 8 | report[11]
            
            self.last_report = report

            self.left_bumper = int(report[14] & 0b1000000 != 0)
            self.right_bumper = int(report[14] & 0b10000000 != 0) #we cast these to int as we use them in non-logic calcs later.

            self.a_button_pressed = report[14] & 0b1 != 0
            self.b_button_pressed = report[14] & 0b10 != 0
            self.x_button_pressed = report[14] & 0b100 != 0
            self.y_button_pressed = report[14] & 0b1000 != 0

            self.start_button_pressed = report[15] & 0b100 != 0
            self.screenshot_button = report[15] & 0b100 != 0
            self.xbox_button = report[15] & 0b1000 != 0

            buttons = ["a", "b", "x", "y", "start", "select", "x", "left_d_pad", "right_d_pad", "screenshot"]
            self.button_flags = {button_name: False for button_name in buttons}

            return True
        
        else:
            return False
        
    def trigger_processer(self):
        output = self.left_trigger - self.right_trigger
        return output


    def deadspot_control(self, raw_controller_input):
        if raw_controller_input < self.deadspot_min or raw_controller_input > self.deadspot_max:
            return raw_controller_input
        else:
            return DEFAULT_JOYSTICK_VALUE
         

    def joystick_processor(self, joystick):
        vertical = self.deadspot_control(joystick["y"]) - DEFAULT_JOYSTICK_VALUE
        horizontal = self.deadspot_control(joystick["x"]) - DEFAULT_JOYSTICK_VALUE

        vertical_processed = int(vertical) # equivilent to dividing by 255
        horizontal_processed = int(horizontal) # equivilent to dividing by 255

        output =  {"x": horizontal_processed, "y": vertical_processed}
        return output


    def processed_controller_output(self) -> List[int]:
        #TODO: refactor to work with pre-processed controller values of 32, not 1024.
        """Returns a processed value for each DoF in a dict"""

        left_joystick_output = self.joystick_processor(self.left_joystick_raw_values)
        right_joystick_output = self.joystick_processor(self.right_joystick_raw_values)

        base_speed = left_joystick_output["x"] >> 10
        shoulder_speed = left_joystick_output["y"] >> 10
        elbow_speed = right_joystick_output["y"] >> 10

        wrist_speed = self.trigger_processer() >> 5
        gripper_speed = (self.left_bumper - self.right_bumper) << 4

        output_list = [base_speed,shoulder_speed,elbow_speed,wrist_speed, gripper_speed]

        return output_list
    

    def input_size_string(self, input_value, input_min, input_max):
        input_range = input_max - input_min
        input_normalised = (input_value - input_min)/input_range

        seperation_left = int(input_normalised * 16)
        seperation_right = 16 - seperation_left

        output = ""
        for i in range(seperation_left):
            output += " "
        output += "|"
        for i in range(seperation_right):
            output += " "
            
        return output
    

    def __str__(self):
        #Horrible string literals.
        output = ""
        output += f"{'Left joystick:':>13}\n"
        output += f"{'':>16}x:{self.left_joystick_raw_values['x']:10.0f}|{self.input_size_string(self.left_joystick_raw_values['x'], 0, MAX_JOYSTICK_VALUE)}"
        output += f"y:{self.left_joystick_raw_values['y']:10.0f}|{self.input_size_string(self.left_joystick_raw_values['y'], 0, MAX_JOYSTICK_VALUE)}\n"

        output += f"{'Right joystick':>13}:\n"
        output += f"{'':>16}x:{self.right_joystick_raw_values['x']:10.0f}|{self.input_size_string(self.right_joystick_raw_values['x'], 0, MAX_JOYSTICK_VALUE)}"
        output += f"y:{self.right_joystick_raw_values['y']:10.0f}|{self.input_size_string(self.right_joystick_raw_values['y'], 0, MAX_JOYSTICK_VALUE)}\n"
    
        output += f"{'triggers':>13}\n"
        output += f"{'left':>16}{self.left_trigger:10.0f}|{self.input_size_string(self.left_trigger, 0, MAX_TRIGGER_VALUE)}\n"
        output += f"{'right':>16}{self.right_trigger:10.0f}|{self.input_size_string(self.right_trigger, 0, MAX_TRIGGER_VALUE)}\n\n"
        output += "bumpers\n"
        output += f"{'left':>16}{self.left_bumper}\n"
        output += f"{'right':>16}{self.right_bumper}\n"
        output += str(self.last_report)
        return output


if __name__ == "__main__":
    
    for device_dict in hid.enumerate():
        keys = list(device_dict.keys())
        keys.sort()
        for key in keys:
            print("%s : %s" % (key, device_dict[key]))
        print()
    controller_values = find_xbox_controller()
    controller = XBoxController(1, controller_values[0], controller_values[1])
    i = 0
    
    max_time_delta = None
    while True:

        start_time = datetime.now()
        new_controller_locations = controller.poll_controller()
        print('\x1b[2J\x1b[H') #code generated by Claude.
        print(controller)
        end_time = datetime.now()
        time_delta = end_time - start_time

        if (max_time_delta == None) or (time_delta > max_time_delta):
            max_time_delta = time_delta


        print(time_delta.microseconds)
        print(max_time_delta.microseconds)
        time.sleep(0.01)