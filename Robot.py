from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos
from Joint import Joint, RevoluteJoint, PrismaticJoint, create_joint_from_robot_config_dict
from typing import List
from time import sleep

ANGLE_UNITS = "°"
DISTANCE_UNITS = "cm"
TIME_UNITS = "ms"

class Robot():
    def __init__(self, name: str, joints: List[Joint]):
        self.name = name
        self.joints = joints

    def print_angle_information(self, debug=False):
        print(f"joint_name\t\tangle/ext({ANGLE_UNITS})\tPWM Value({TIME_UNITS})")
        for joint in self.joints:
            joint.print_table_view()

    def update_joint_target_angle(self, new_angle):
        """Updates the target angles of the joint to some new position. ens"""

def create_joint_list_from_config_file(filename):
    joint_dicts = config_scripts.load_config_file_from_yaml(filename)
    joints = list(map(create_joint_from_robot_config_dict, joint_dicts))
    return joints

if __name__ == "__main__":
    robot_joints = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")
    robot = Robot("Vanessa", robot_joints)
    try:
        while True:
            robot.joints[1].servo_motor.duty_cycle += 2
            robot.print_angle_information()
            sleep(0.3)
            os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        print("______________________\nprocess terminated")
    finally:
        print(robot.print_angle_information())