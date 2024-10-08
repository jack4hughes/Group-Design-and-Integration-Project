from ServoMotor import ServoMotor
import config_scripts
from config_scripts import ServoMotor
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos

CONFIG_FOLDER_LOCATION = "Motor Config Files"
ROBOT_CONFIG_FILE_NAME =  "robot_setup_config.yaml"
config_file_location = os.path.join(CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME)

def create_dh_matrix_from_dict(dh_dict: dict) -> np.array:
        """Takes in a dictionary of Denavit Hartenburg values and returns a 4x4 numpy array of the Denavit Hartenburg matrix for the joint."""
        
        joint_angle = dh_dict["joint_angle"]
        joint_distance = dh_dict["joint_distance"]
        common_normal_length = dh_dict["common_normal_length"]
        link_twist_angle = dh_dict["link_twist_angle"]

        #TODO: Double check this!
        dh_matrix = np.array(
            [[cos(joint_angle), -sin(joint_angle),0,common_normal_length],
             [sin(joint_angle)*cos(link_twist_angle), cos(joint_angle)*cos(link_twist_angle), -sin(link_twist_angle), -sin(common_normal_length)*joint_distance],
             [sin(joint_angle)*sin(link_twist_angle), cos(joint_angle)*sin(link_twist_angle), cos(link_twist_angle),  cos(common_normal_length)*joint_distance],
             [0,0,0,1]]
            )
        
        return dh_matrix

class Joint:
    """A Joint is an object that combines a servo motor with a distance & pose relative the previous joint in our robot..
     We use this to calculate and affect the trajectory of our robot, instead of touching the servos directly."""
    
    def __init__(self, config_dict = None):
        servo_config_file_location = os.path.join(CONFIG_FOLDER_LOCATION, config_dict["servo_config_file"])
        servo_config_dict = config_scripts.load_config_file_from_yaml(servo_config_file_location)
        self.servo_motor = ServoMotor(config_dict["pwm_pin"], servo_config_dict)

        self.initial_dh_dict = config_dict["dh_values"]
        self.initial_dh_matrix = create_dh_matrix_from_dict(self.initial_dh_dict)
        self.current_dh_matrix = self.initial_dh_matrix
        self.target_dh_matrix = self.initial_dh_matrix


class RevoluteJoint(Joint):
    """A joint which revolves around a point. For our robot that means the shoulder, elbow, and wrist joints"""
    def __init__(self, config_dict):
        super().__init__(self, config_dict)
        self.min_joint_angle = config_dict["min_joint_angle"] #the minimum physically possible angle for the joint.
        self.max_joint_angle = config_dict["max_joint_angle"] #the maximum physically possible angle for the joint.
        self.current_joint_angle = 0

    def convert_pwm_to_angle(self, pwm):
        """Converts a raw PWM value into an angle."""
        pass
    
    def convert_angle_to_pwm(self, angle):
        """Converts an angular value to PWM"""
        pass

    def update_target_pwm(self, pwm_value):
        """updates the target pwm value of our joint"""

    

class PrismaticJoint(Joint):
    """A Joint that moves in a straight line. This is used for our gripper."""
    def __init__(self, config_dict):
        super().__init__(self, config_dict)
        self.min_joint_extension = config_dict["min_joint_extension"]
        self.min_joint_extension = config_dict["max_joint_extension"]
    

if __name__ == "__main__":
    config_dict = config_scripts.load_config_file_from_yaml(config_file_location)
    shoulder_joint_config_dict = config_dict[0]
    shoulder_joint = Joint(shoulder_joint_config_dict)
    
    print(shoulder_joint.initial_dh_dict)
    print(create_dh_matrix_from_dict(shoulder_joint.initial_dh_dict))

