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

DEFAULT_JOYSTICK_VALUE = 127
MAX_JOYSTICK_VALUE = 255
MAX_TRIGGER_VALUE = 3
DEADSPOT_SIZE = 10

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

        self.deadspot_min = DEFAULT_JOYSTICK_VALUE - DEADSPOT_SIZE
        self.deadspot_max = DEFAULT_JOYSTICK_VALUE + DEADSPOT_SIZE

        self.left_joystick_buffer = create_joystick_buffer_dict(100)
        self.right_joystick_buffer = create_joystick_buffer_dict(100)
        self.last_report = None

    def poll_controller(self): 
        """updates controller inputs if controller is found."""
        report = self.hid_input.read(64) #reads relevant bytes
        if len(report) > 10:
            self.left_joystick_raw_values["x"] = report[2]
            self.left_joystick_raw_values["y"] = report[4]

            self.right_joystick_raw_values["x"] = report[6]
            self.right_joystick_raw_values["y"] = report[8]

            self.left_trigger = report[10]
            self.right_trigger = report[12]
            
            self.last_report = report

            if report[15] == 64:
                self.left_trigger_button = 1
            if report[15] == 128:
                self.right_trigger_button = 1
            else:
                self.left_trigger = 0
                self
            return True
        else:
            return False
        
    def trigger_processer(self):
        output = self.left_trigger - self.right_trigger
        return output * 5

    def deadspot_control(self, raw_controller_input):
        if raw_controller_input < self.deadspot_min or raw_controller_input > self.deadspot_max:
            return raw_controller_input
        else:
            return DEFAULT_JOYSTICK_VALUE
         

    def joystick_processor(self, joystick):
        vertical = self.deadspot_control(joystick["y"]) - DEFAULT_JOYSTICK_VALUE
        horizontal = self.deadspot_control(joystick["x"]) - DEFAULT_JOYSTICK_VALUE

        vertical_processed = int(vertical/16)
        horizontal_processed = int(horizontal/16)

        output =  {"x": horizontal_processed, "y": vertical_processed}
        return output

    def normalised_controller_output(self) -> List[int]:

        left_joystick_output = self.joystick_processor(self.left_joystick_raw_values)
        right_joystick_output = self.joystick_processor(self.right_joystick_raw_values)

        base_speed = left_joystick_output["x"]
        shoulder_speed = left_joystick_output["y"]

        elbow_speed = right_joystick_output["y"]
        wrist_speed = right_joystick_output["x"]

        gripper_speed = self.trigger_processer()

        output_list = [base_speed,shoulder_speed,elbow_speed,wrist_speed, 0]

        return output_list
    

    def update_joints(self):
        """This is the function that will update our target_pwm values using """ 


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
        output += f"{'':>16}x:{self.left_joystick_raw_values['x']:>4}|{self.input_size_string(self.left_joystick_raw_values['x'], 0, MAX_JOYSTICK_VALUE)}"
        output += f"y:{self.left_joystick_raw_values['y']:>4}|{self.input_size_string(self.left_joystick_raw_values['y'], 0, MAX_JOYSTICK_VALUE)}\n"

        output += f"{'Right joystick':>13}:\n"
        output += f"{'':>16}x:{self.right_joystick_raw_values['x']:>4}|{self.input_size_string(self.right_joystick_raw_values['x'], 0, MAX_JOYSTICK_VALUE)}"
        output += f"y:{self.right_joystick_raw_values['y']:>4}|{self.input_size_string(self.right_joystick_raw_values['y'], 0, MAX_JOYSTICK_VALUE)}\n"
    
        output += f"{'bumpers':>13}\n"
        output += f"{'left':>16}{self.left_trigger:>6}|{self.input_size_string(self.left_trigger, 0, MAX_TRIGGER_VALUE)}\n"
        output += f"{'right':>16}{self.right_trigger:>6}|{self.input_size_string(self.right_trigger, 0, MAX_TRIGGER_VALUE)}\n\n"
        output += str(self.last_report)
        return output


if __name__ == "__main__":
    buffer = CircularBuffer()
    
    for device_dict in hid.enumerate():
        keys = list(device_dict.keys())
        keys.sort()
        for key in keys:
            print("%s : %s" % (key, device_dict[key]))
        print()

    controller = XBoxController(1)
    i = 0

    print(buffer)

    while True:
        new_controller_locations = controller.poll_controller()
        print(controller)
        print()
        time.sleep(0.001)