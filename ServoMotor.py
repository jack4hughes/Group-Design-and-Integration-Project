import config_scripts
import os
import pprint
import yaml
import numpy as np
from numpy import sin, cos  
from typing import Union
import typing

class ServoMotor:
    # servo motor refactored to take in an unpacked dict.
    def __init__(self,
                 config_info: Union[str, dict, None] = None,
                 degrees_of_movement: int = None,
                 duty_cyle_ms: float = None,
                 max_angle_duty_cycle_ms: float = None,
                 max_degree_value: float = None,
                 min_angle_duty_cycle_ms: float = None,
                 min_degree_value: float = None,
                 servo_name: str = None,
                 servo_type: str = "Unknown",
                 torque: float = None,
                 volts: float = None,
                 pin_out: float= None,
                 **kwargs) -> None:

        if type(config_info) == str:
            config_info = config_scripts.load_config_file_from_yaml(config_info)
            self.__init__(**config_info)

        if type(config_info) == dict:
            self.__init__(**config_info)

        else:
            self.servo_name = servo_name
            self.servo_type = servo_type
            
            self.max_angle_duty_cycle_ms = max_angle_duty_cycle_ms
            self.max_degree_value = max_degree_value
            
            self.min_angle_duty_cycle_ms = min_angle_duty_cycle_ms
            self.min_degree_value = min_degree_value
            
            self.degrees_of_movement = degrees_of_movement
            self.duty_cyle_ms = duty_cyle_ms

            self.torque = torque
            self.volts = volts
            self.pin_out = pin_out

        self.other_info = kwargs
    
    def update_position(new_position_pwm_value):
        """Updates the position of our servo based directly off of PWM values. This is how we actually move the motors."""
        pass

    def __str__(self):
        output = f"{self.servo_name} information:\n\n"
        for item in dir(self):
            if "__" not in item:
                output += f"\t{item}\t{getattr(self, item, 'Not Initialised')}\n"

        return output

def create_servo(config_file_location: Union[str, None], **args) -> dict:
    """Creates a configured servo from a config file location and keywords. any keywords will overwrite """
    if config_file_location != None:
        config_args = config_scripts.load_config_file_from_yaml(config_file_location)
    
        

if __name__ == "__main__":
    test_servo_config_file_location = os.path.join("Motor Config Files", "servo_1_config.yaml")
    test_servo_dict = config_scripts.load_config_file_from_yaml(test_servo_config_file_location)

    #testing that strings and dicts can be entered.
    servo1 = ServoMotor(test_servo_config_file_location)
    servo2 = ServoMotor(test_servo_dict)

    print(servo1)