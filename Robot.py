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
from SerialJointUpdateInterface import SerialServoPositionUpdater

ANGLE_UNITS = "°"
DISTANCE_UNITS = "cm"
TIME_UNITS = "ms"
SERIAL_PORT = "/dev/tty.usbserial-AB0NBPCE"

class Robot():
    def __init__(self, name: str, joints: Collection[Union[RevoluteJoint, PrismaticJoint]], servo_angle_updater: SerialServoPositionUpdater):
        self.name = name
        self.joints = joints
        self.servo_angle_updater = servo_angle_updater


    def print_joint_information(self, debug=False):
        print(f"joint_name\t\tangle/ext({ANGLE_UNITS})\tPWM Value({TIME_UNITS})")
        for joint in self.joints:
            joint.print_table_view()


    def send_joint_update_message(self, target_joint_id: int):
        """Sends a message that updates a joint to the current PWM value stored in its ServoMotor object."""

        joint: Joint = self.joints[target_joint_id]

        self.servo_angle_updater.update_servo(target_joint_id, joint.servo_motor.duty_cycle)


    def turn_servo_off(self, target_joint_id: int) -> None:
        """turns the selected joints servo motor off (sets PWM to 0.)"""
        self.servo_angle_updater()
        self.send_joint_update_message()
    
    def update_joints_from_controller_output(self, controller_output_list: dict) -> None:
        """ 
        takes a list from our controller object with the processed controller output and uses
        that list to update each joints PWM value."""

        for joint, speed in zip(self.joints, controller_output_list):
            current_position = joint.servo_motor.duty_cycle
            target_position = current_position + speed
            joint.update_pwm(target_position)


def create_joint_list_from_config_file(filename):
    joint_dicts = config_scripts.load_config_file_from_yaml(filename)
    joints = list(map(create_joint_from_robot_config_dict, joint_dicts))
    return joints


def create_joint_from_dict(joint_dict) -> Union[PrismaticJoint, RevoluteJoint]:
    joint_type = joint_dict["joint_type"]
    if joint_type in "revolute":
        joint = RevoluteJoint(**joint_dict)
    if joint_type in "prismatic":
        joint = PrismaticJoint(**joint_dict)
    else:
        raise TypeError("Robot must have a joint type of 'revolute' or 'prismatic' in joint config file")
    return joint


if __name__ == "__main__":
    serial_port = SerialServoPositionUpdater(SERIAL_PORT)
    robot_joints = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")
    robot = Robot("Vanessa", robot_joints, serial_port)
    robot.print_joint_information()
    
    robot.joints[0].update_angle(0)
    robot.joints[1].update_angle(0)
    robot.joints[3].update_angle(0)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)
    robot.send_joint_update_message(3)
    robot.send_joint_update_message(4)
    
    sleep(1)
    robot.joints[0].update_angle(10)
    robot.joints[1].update_angle(10)
    robot.joints[3].update_angle(10)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)
    robot.send_joint_update_message(3)
    robot.send_joint_update_message(4)

    sleep(1)
    robot.joints[0].update_angle(20)
    robot.joints[1].update_angle(20)
    robot.joints[3].update_angle(20)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)
    robot.send_joint_update_message(3)
    robot.send_joint_update_message(4)

    sleep(1)
    robot.joints[0].update_angle(30)
    robot.joints[1].update_angle(30)
    robot.joints[3].update_angle(30)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)
    robot.send_joint_update_message(3)
    robot.send_joint_update_message(4)
    
    print("\n")
    robot.print_angle_information()