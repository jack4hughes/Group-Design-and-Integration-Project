from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos
from Joint import Joint, RevoluteJoint, PrismaticJoint, create_joint_from_robot_config_dict
from typing import List

class Robot():
    def __init__(self, name: str, joints: List[Joint]):
        self.name = name
        self.joints = joints

    def print_angle_information(self, debug=False):
        for joint in self.joints:
            print(joint)

def create_joint_list_from_config_file(filename):
    joint_dicts = config_scripts.load_config_file_from_yaml(filename)
    joints = list(map(create_joint_from_robot_config_dict, joint_dicts))
    return joints

if __name__ == "__main__":
    robot_joints = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")
    robot = Robot("Vanessa", robot_joints)

    robot.print_angle_information(debug=True)