from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import numpy as np
from numpy import sin, cos  
from Helper import ANGLE_UNITS, TIME_UNITS, DISTANCE_UNITS, CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME
from Helper import scale_transform

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
    
    def __init__(self,
                 name: str = None,
                 joint_type = None,
                 servo_config_file: str = None,
                 servo_motor: ServoMotor = None,
                 initial_dh_dict: dict = None,
                 pwm_pin = None,
                 ):

        self.name = name
        
        if servo_motor == None:
            if servo_config_file == None:
                raise ValueError("Could not configure a servo motor for the joint!")
            servo_dict = config_scripts.load_config_file_from_yaml("Motor Config Files/" + servo_config_file)
            self.servo_motor = ServoMotor(servo_dict)

        self.inital_dh_dict = initial_dh_dict

class RevoluteJoint(Joint):
    """A joint which revolves around a point. For our robot that means the shoulder, elbow, and wrist joints"""
    def __init__(self,
                 initial_angle: float = None,
                 min_angle: float = None,
                 max_angle: float = None,
                 
                 name: str = None,
                 joint_type = None,
                 servo_config_file: str = None,
                 servo_motor: ServoMotor = None,
                 initial_dh_dict: dict = None,
                 pwm_pin = None,
                 ):
        
        super().__init__(name,
                         joint_type,
                         servo_config_file,
                         servo_motor,
                         initial_dh_dict,
                         pwm_pin)
        
        self.min_angle = min_angle
        self.max_angle = max_angle

        self.min_pwm = self.servo_motor.angle_to_pwm(min_angle)
        self.max_pwm = self.servo_motor.angle_to_pwm(max_angle)

        self.initial_angle = initial_angle
        self.angle = initial_angle
    
    def __str__(self):
        output = ""
        output += f"{self.name}:\n"
        output += f"current angle: {self.angle}{ANGLE_UNITS}\t\t{self.servo_motor.duty_cycle}{TIME_UNITS}\n"
        return output
    

    def update_angle(self, target_angle) -> None:
        if self.min_angle > target_angle or self.max_angle < target_angle:
            raise ValueError(f"Impossible angle: the angle provided is outside of our joint constraints. angle: {target_angle} min_val: {self.min_angle} max_val: {self.max_angle}")
            return
        
        self.angle = target_angle
        target_pwm = self.servo_motor.angle_to_pwm(target_angle)
        self.servo_motor.update_pwm_control_value(target_pwm)
    
    def update_pwm(self, target_pwm) -> None:
        target_angle = self.servo_motor.pwm_to_angle(target_pwm)
        if self.min_pwm > target_pwm or self.max_pwm < target_pwm:
            raise ValueError(f"Impossible angle: the angle provided is outside of our joint constraints. angle: {self.servo_motor.pwm_to_angle(target_pwm)} min_val: {self.min_angle} max_val: {self.max_angle}")
            return
        
        self.servo_motor.update_pwm_control_value(target_pwm)
        self.angle = target_angle
        
    def increase_pwm_by_x(self, input_size):
        """Adds input_size to the current PWM value. Used for controller motion."""
        current_duty_cycle = self.servo_motor.duty_cycle
        self.update_pwm(current_duty_cycle + input_size)
        return
    

    def print_table_view(self):
        print_string = f"{self.name:15}{self.angle}{ANGLE_UNITS:10}{self.servo_motor.duty_cycle}{TIME_UNITS:10}"
        print(print_string)

class PrismaticJoint(Joint):
    """A Joint that moves in a straight line. This is used for our gripper."""
    def __init__(self,
                initial_extension: float = None,
                min_extension: float = None,
                max_extension: float = None,
                
                name: str = None,
                joint_type = None,
                servo_config_file: str = None,
                servo_motor: ServoMotor = None,
                initial_dh_dict: dict = None,
                pwm_pin = None,
                ):
        
        super().__init__(name,
                         joint_type,
                         servo_config_file,
                         servo_motor,
                         initial_dh_dict,
                         pwm_pin)
        
        self.min_extension = min_extension
        self.max_extension = max_extension
        self.initial_extension = initial_extension
        self.extension = initial_extension
    
    def __str__(self):
        output = ""
        output += f"{self.name}:\n"
        output += f"current distance: {self.extension}{DISTANCE_UNITS:10}\t{self.servo_motor.duty_cycle}{TIME_UNITS:10}"
        return output
    
    def update_angle(self, target_position) -> None:
        if self.min_extension > target_position or self.max_extension < target_position:
            raise ValueError(f"Impossible position: the position provided is outside of our joint constraints. position: {target_position} min_val: {self.min_extension} max_val: {self.max_extension}")
            return
        
        self.extension = target_position
        target_pwm = scale_transform(target_position, (self.min_extension, self.max_extension), self.servo_motor.duty_cycle_range)
        self.servo_motor.update_pwm_control_value(target_pwm)
    
        def update_pwm(self, target_pwm) -> None:
            target_pwm = self.servo_motor.angle_to_pwm(target_pwm)
            if self.min_pwm > target_pwm or self.max_pwm < target_pwm:
                raise ValueError(f"Impossible angle: the angle provided is outside of our joint constraints. angle: {self.servo_motor.pwm_to_angle(target_pwm)} min_val: {self.min_angle} max_val: {self.max_angle}")
                return
            
            self.angle = self.servo_motor.pwm_to_angle(target_pwm)
            self.servo_motor.update_pwm_control_value(target_pwm)
            
    def print_table_view(self):
        print_string = f"{self.name:15}{self.extension}{DISTANCE_UNITS:10}{self.servo_motor.duty_cycle}{TIME_UNITS:10}"
        print(print_string)

def create_joint_from_robot_config_dict(joint_information_dict):
    if joint_information_dict["joint_type"] == "revolute":
        return RevoluteJoint(**joint_information_dict)
    elif joint_information_dict["joint_type"] == "prismatic":
        return PrismaticJoint(**joint_information_dict)
    
if __name__ == "__main__":
    joint_info_dicts = config_scripts.load_config_file_from_yaml("Motor Config Files/robot_setup_config.yaml")
    joints = [create_joint_from_robot_config_dict(joint_info_dict) for joint_info_dict in joint_info_dicts]

    for joint in joints:
        print(joint)