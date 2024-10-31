from Helper import scale_transform
import config_scripts
import os
import pprint
import yaml
import numpy as np
from numpy import sin, cos  
from typing import Union, Collection
import typing
#from machine import Pin    only enable for micropython build.

class ServoMotor:
    # servo motor refactored to take in an unpacked dict.
    def __init__(self,
                 config_info: Union[str, dict, None] = None,
                 range_of_motion: Collection[Union[int, float]]= None,
                 duty_cycle_range: Collection[Union[int, float]] = None,
                 initial_duty_cycle: float = None,
                 servo_name: str = None,
                 servo_type: str = "Unknown",
                 torque: float = None,
                 volts: float = None,
                 pin_out = None,
                 **kwargs) -> None:

        if type(config_info) == str:
            config_info = config_scripts.load_config_file_from_yaml(config_info)
            self.__init__(**config_info)

        if type(config_info) == dict:
            self.__init__(**config_info)

        else:
            self.servo_name = servo_name
            self.servo_type = servo_type

            self.duty_cycle_range = duty_cycle_range
            self.range_of_motion = range_of_motion
            self.duty_cycle = initial_duty_cycle
            self.torque = torque
            self.volts = volts
            self.pin_out = pin_out

            # self.pwm_control = self.create_pwm_pin(self, pin_number = self.pin_out)
        self.other_info = kwargs

    def __str__(self):
        output = f"{self.servo_name} information:\n\n"
        for item in dir(self):
            if "__" not in item:
                output += f"\t{item}\t{getattr(self, item, 'Not Initialised')}\n"

        return output
    
    def update_pwm_control_value(self, pwm_value: Union[int, float]) -> None:
        """Updates the duty cycle of the servo, changing its positon.
        
        NOTE: we should never change this directly when testing an assembled robot, instead servos should be attached to 
        Joint objects first, then we can use the methods to adjust each joint. If the PWM duty cycle or pulse width for the servo 
        is changed directly the corresponding joint angle will not be updated, resulting in unpredictable behavhior."""
        
        if pwm_value < self.duty_cycle_range[0] or pwm_value > self.duty_cycle_range[1]:
            raise ValueError("The PWM specified is outside of this servos operating range.")
        
        self.duty_cycle = int(pwm_value) # makes sure duty cycle does not exceed servo limits.
        return

    def angle_to_pwm(self, angle: Union[int, float]) -> Union[int, float]:
        """Calculates PWM values from angles, maybe PWM should be done directly if used often."""
        return scale_transform(angle, self.range_of_motion, self.duty_cycle_range)

    def pwm_to_angle(self, pwm: Union[int, float]) -> Union[int, float]:
        return scale_transform(pwm, self.duty_cycle_range, self.range_of_motion)
    
if __name__ == "__main__":
    test_servo_config_file_location = os.path.join("Motor Config Files", "servo_1_config.yaml")
    test_servo_dict = config_scripts.load_config_file_from_yaml(test_servo_config_file_location)

    #testing that strings and dicts can be entered.
    servo1 = ServoMotor(test_servo_config_file_location)
    servo2 = ServoMotor(test_servo_dict)