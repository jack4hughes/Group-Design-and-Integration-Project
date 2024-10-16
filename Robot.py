from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos
from Joint import Joint, RevoluteJoint, PrismaticJoint, create_joint_from_robot_config_dict
from typing import Collection, Union
from time import sleep

ANGLE_UNITS = "°"
DISTANCE_UNITS = "cm"
TIME_UNITS = "ms"

class Robot():
    def __init__(self, name: str, joints: Collection[Union[RevoluteJoint, PrismaticJoint]]):
        self.name = name
        self.joints = joints

    def print_joint_angle_information(self, debug=False):
        print(f"joint_name\t\tangle/ext({ANGLE_UNITS})\tPWM Value({TIME_UNITS})")
        for joint in self.joints:
            joint.print_table_view()

    def string_output(self):
        #0 P 1500 #1 P 1500 #2 P 1500 #3 P 1500 #4 P 1500 #5 P 1500)
        output = ""
        for list_index, joint in enumerate(self.joints):
           duty_cyle = joint.servo_motor.duty_cycle
           output += f"#{list_index} P {duty_cyle} "
        output += "\r"
        
        return output

def create_joint_list_from_config_file(filename):
    joint_dicts = config_scripts.load_config_file_from_yaml(filename)
    joints = list(map(create_joint_from_robot_config_dict, joint_dicts))
    return joints

if __name__ == "__main__":
    robot_joints = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")
    robot = Robot("Vanessa", robot_joints)
    string = robot.string_output()
    print(string)