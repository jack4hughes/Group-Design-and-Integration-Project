from Robot import Robot
from Joint import PrismaticJoint, RevoluteJoint
from inputs import devices
import hid
import os
import time

class Controller:
    def __init__(self, robot: Robot, start_bin = 0x045e, end_bin = 0x0b13):
      self.hid_input = hid.device()
      print(self.hid_input)
      self.hid_input.open(start_bin, end_bin)
      print(type(self.hid_input))
      self.hid_input.set_nonblocking(True)
      
      self.left_joystick = {"x": 0, "y": 0} #sets up dict
      self.right_joystick = {"x": 0, "y": 0}

      self.left_bumper = 0
      self.right_bumper = 0

      self.a_button = 0
      self.b_button = 0
    
    def poll_controller(self): 
        """updates controller inputs if controller is found."""
        report = self.hid_input.read(64) #reads relevant bytes

        if report:
            self.left_joystick["x"] = report[2]
            self.left_joystick["y"] = report[4]


            self.right_joystick["x"] = report[6]
            self.right_joystick["y"] = report[8]

            self.left_bumper = report[9]
            self.right_bumper = report[11]
            return True
        else:
            return False

    def update_joints(self):
        """This is the function that will update our target_pwm values using """ 
        pass

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
        output = ""
        output += f"{'Left joystick':>15}:\n"
        output += f"{'':>19}x: {self.input_size_string(self.left_joystick['x'], 0, 255)}"
        output += f"y: {self.input_size_string(self.left_joystick['y'], 0, 255)}\n"

        output += f"{'Right joystick':>15}\n"
        output += f"{'':>19}x: {self.input_size_string(self.right_joystick['x'], 0, 255)}"
        output += f"y: {self.input_size_string(self.right_joystick['y'], 0, 255)}\n"

        
        output += f"\n{self.input_size_string(self.left_bumper, 0, 255)}\n"
        output += f"\n{self.input_size_string(self.right_bumper, 0, 255)}\n"
        return output


if __name__ == "__main__":
    for device in hid.enumerate():
        print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

    controller = Controller(1)
    while True:
        right_bumper_position = 9
        new_controller_locations = controller.poll_controller()
        print(controller)
        time.sleep(0.01)
        print("\033[2J\033[H")