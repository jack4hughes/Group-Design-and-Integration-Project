from ServoMotor import ServoMotor
import config_scripts
import os
from pprint import pprint
import yaml
import pprint
import numpy as np
from numpy import sin, cos  
from ServoMotor import ANGLE_UNITS, TIME_UNITS, DISTANCE_UNITS, CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME
from ServoMotor import scale_transform

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
                 initial_pwm: int = None,
                 servo_config_file: str = None,
                 servo_motor: ServoMotor = None,
                 initial_dh_dict: dict = None,
                 pwm_pin = None,
                 max_motor_speed = 8,
                 ):
        
        self.speed_reduction = 32/max_motor_speed
        self.pwm_angle_calibration_correction = 1500 - initial_pwm
        self.name = name

        if servo_motor == None:
            print("Servo motor not found")
            if servo_config_file == None:
                raise ValueError("Could not configure a servo motor for the joint!")
            
            print(servo_config_file)
            servo_dict = config_scripts.load_config_file_from_yaml("Motor Config Files/" + servo_config_file)
            self.servo_motor = ServoMotor(servo_dict)
        else:
            print(servo_motor)
        self.servo_motor.duty_cycle = initial_pwm

        self.inital_dh_dict = initial_dh_dict

    def rotate(self, degrees):
        raise NotImplementedError

    def extend(self, degrees):
        raise NotImplementedError

class RevoluteJoint(Joint):
    """A joint which revolves around a point. For our robot that means the shoulder, elbow, and wrist joints"""
    def __init__(self,
                 initial_angle: float = None,
                 min_angle: float = None,
                 max_angle: float = None,
                 initial_pwm: int = None, #initial PWM to set motor to desired point.
                 name: str = None,
                 joint_type = None,
                 servo_config_file: str = None,
                 servo_motor: ServoMotor = None,
                 initial_dh_dict: dict = None,
                 pwm_pin = None,
                 max_motor_speed = 8
                 ):

        super().__init__(name,joint_type,initial_pwm, servo_config_file, servo_motor, initial_dh_dict, pwm_pin, max_motor_speed)
        self.min_pwm = self.servo_motor.angle_to_pwm(min_angle)
        self.max_pwm = self.servo_motor.angle_to_pwm(max_angle)

        self.working_range = (min_angle, max_angle)
        self.min_angle = self.working_range[0]
        self.max_angle = self.working_range[1]

        self.initial_angle = initial_angle
        self.angle = initial_angle
    
    def __str__(self):
        output = ""
        output += f"{self.name}:\n"
        output += f"current angle: {self.angle}{ANGLE_UNITS}\t\t{self.servo_motor.duty_cycle}{TIME_UNITS}\n"
        return output
    
    def rotate(self, degrees):
        pass
        
    
    def get_angle(self, pwm: int = None) -> float:
        print(self.initial_angle)
        return self.servo_motor.pwm_to_angle(self.servo_motor.duty_cycle + self.pwm_angle_calibration_correction)



    def update_angle(self, target_angle) -> None:

        if self.min_angle> target_angle or self.max_angle < target_angle:
            raise ValueError(f"Impossible angle: the angle provided is outside of our joint constraints. angle: {target_angle} min_val: {self.min_angle} max_val: {self.max_angle}")
            return

        self.angle = target_angle
        target_pwm = self.servo_motor.angle_to_pwm(target_angle) + self.pwm_angle_calibration_correction
        self.servo_motor.update_pwm_control_value(target_pwm)

        if self.min_pwm > target_pwm or self.max_pwm < target_pwm:
            raise ValueError(f"Impossible PWM: the PWM provided is outside of our joint constraints. angle: {target_pwm} min_val: {self.min_pwm} max_val: {self.max_pwm}")
            return
        
    
    def update_pwm(self, target_pwm) -> None:
        target_angle = self.get_angle(target_pwm)
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
        print_string = f"{self.name:15}{self.angle:10.2f}{ANGLE_UNITS:10}{self.servo_motor.duty_cycle:5}{TIME_UNITS:10}"
        print(print_string)

class PrismaticJoint(Joint):
    """A Joint that moves in a straight line. This is used for our gripper."""
    #TODO map PrismaticJoint update PWM method to extension.
    def __init__(self,
                initial_extension: float = None,
                min_extension: float = 0,
                max_extension: float = None,
                angular_velocity: float = None,
                name: str = None,
                joint_type: str = None,
                servo_config_file: str = None,
                servo_motor: ServoMotor = None,
                initial_dh_dict: dict = None,
                pwm_pin = None,
                ):
        
        super().__init__(name,
                         joint_type,
                         angular_velocity,
                         servo_config_file,
                         servo_motor,
                         initial_dh_dict,
                         pwm_pin)
            
        self.min_extension = min_extension
        self.max_extension = max_extension
        self.initial_extension = initial_extension
        self.extension = initial_extension

        self.min_pwm = self.servo_motor.duty_cycle_range[0]
        self.max_pwm = self.servo_motor.duty_cycle_range[1]

    
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


    def update_pwm(self, target_pwm) -> None:
        if self.min_pwm > target_pwm or self.max_pwm < target_pwm:
            raise ValueError(f"Impossible angle: the angle provided is outside of our joint constraints. angle: {self.get_angle(target_pwm)} min_val: {self.min_angle} max_val: {self.max_angle}")
            return
        
        self.servo_motor.update_pwm_control_value(target_pwm)
               
    def print_table_view(self):
        print_string = f"{self.name:15}{self.extension}{DISTANCE_UNITS:10}{self.servo_motor.duty_cycle}{TIME_UNITS:10}"
        print(print_string)

def create_joint_from_robot_config_dict(joint_information_dict):
    if joint_information_dict["joint_type"] == "revolute":
        print(joint_information_dict)
        return RevoluteJoint(**joint_information_dict)
    elif joint_information_dict["joint_type"] == "prismatic":
        return PrismaticJoint(**joint_information_dict)
    
if __name__ == "__main__":
    joint = RevoluteJoint(0,-90,90,1600,"test_joint","Prismatic","servo_1_config.yaml")
    print(joint)
    print(joint.get_angle())