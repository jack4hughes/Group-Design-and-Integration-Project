from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos
from Joint import Joint, RevoluteJoint, PrismaticJoint
from typing import List

class Robot():
    def __init__(self, config_dict=None, config_file_location = None):
        robot_joint_cofig_dicts = config_scripts.load_joint_configs_from_config_file("Motor Config Files/robot_setup_config.yaml")
        self.joint_list = [Joint(config_dict = robot_joint_cofig_dict) for robot_joint_cofig_dict in robot_joint_cofig_dicts]

def find_end_effector_location(self):
for joint in robot_joint_list:
    print(joint.joint_name)
    print(joint.initial_dh_matrix)
    print("\n")