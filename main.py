from serial import Serial
from ServoMotor import ServoMotor
from pprint import pprint
from time import time
from Helper import ANGLE_UNITS, TIME_UNITS, DISTANCE_UNITS, CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME
from time import sleep
import os
from GeneratePaths import lerp_path_generator, triangle_loop, safe_path_to_initial_point_in_trajectory
from  Robot import Robot, create_joint_list_from_config_file, create_joint_from_dict
from SerialJointUpdateInterface import SerialServoPositionUpdater, ServoPositionUpdater
from itertools import cycle, chain
from Joint import PrismaticJoint, RevoluteJoint
import config_scripts

REFRESH_FREQUENCY = 0.025 # 25 ms so 40 commands per second.

def loop_until_keyboard_interrupt(func):
    def main_loop_wrapper(*args):
        try:
            while True:
                #prints the robots servo angle information.
                func(*args)
                sleep(REFRESH_FREQUENCY)
                os.system('cls' if os.name == 'nt' else 'clear')
        except KeyboardInterrupt:
            print("______________________\nprocess terminated")
        except GeneratorExit:
            print("move complete")
        finally:
            pass
    return main_loop_wrapper

@loop_until_keyboard_interrupt
def angle_update_loop(robot: Robot, base_rotation_generator, shoulder_rotation_generator, elbow_rotation_generator) -> None:
    start_time = time()

    next_location_base = next(base_rotation_generator)
    next_location_shoulder = next(shoulder_rotation_generator)
    next_location_elbow = next(elbow_rotation_generator)

    robot.joints[0].update_angle(next_location_base)
    robot.joints[1].update_angle(next_location_shoulder)
    robot.joints[2].update_angle(next_location_elbow)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)

    robot.print_joint_information()
    end_time = time()
    total_time_elapsed = end_time - start_time
    percentage_of_loop = total_time_elapsed*100/REFRESH_FREQUENCY #used to make sure we arent doing too many calculations.
    print(f"percentage of loop time calculating:  {percentage_of_loop:.3f}%")
    
@loop_until_keyboard_interrupt
def controller_input(robot: Robot, base_rotation_generator, shoulder_rotation_generator, elbow_rotation_generator) -> None:


    for joint_number, joint in enumerate(Robot.joints):
        robot.send_joint_update_message(joint_number)

    robot.print_joint_information()

@loop_until_keyboard_interrupt
def pwm_update_loop(robot: Robot, base_rotation_generator, shoulder_rotation_generator, elbow_rotation_generator) -> None:
    start_time = time()

    next_location_base = next(base_rotation_generator)
    next_location_shoulder = next(shoulder_rotation_generator)
    next_location_elbow = next(elbow_rotation_generator)

    robot.joints[0].update_pwm(next_location_base)
    robot.joints[1].update_pwm(next_location_shoulder)
    robot.joints[2].update_pwm(next_location_elbow)

    robot.send_joint_update_message(0)
    robot.send_joint_update_message(1)
    robot.send_joint_update_message(2)

    robot.print_joint_information()
    end_time = time()
    total_time_elapsed = end_time - start_time
    percentage_of_loop = total_time_elapsed*100/REFRESH_FREQUENCY #used to make sure we arent doing too many calculations.
    print(f"percentage of loop time calculating:  {percentage_of_loop:.3f}%")
    
if __name__ == "__main__":
    #initialises robot.
    try:
        serial_out = SerialServoPositionUpdater("/dev/tty.usbserial-AB0NBPCE", 115200)
    except:
        serial_out = ServoPositionUpdater()
        print("robot couldn't be found! simulating joint movement")
    robot_joint_info = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")
    robot = Robot("Vanessa", robot_joint_info, serial_out)
    print("robot initialised!")

    #initialises paths

    base_path_min = int(robot.joints[0].servo_motor.angle_to_pwm(-30))
    base_path_max = int(robot.joints[0].servo_motor.angle_to_pwm(30))

    shoulder_path_min = int(robot.joints[1].servo_motor.angle_to_pwm(-10))
    shoulder_path_max = int(robot.joints[1].servo_motor.angle_to_pwm(10))

    elbow_path_min = int(robot.joints[2].servo_motor.angle_to_pwm(-10))
    elbow_path_max = int(robot.joints[2].servo_motor.angle_to_pwm(10))

    base_path = safe_path_to_initial_point_in_trajectory(1500, triangle_loop(base_path_min, base_path_max, 2))
    shoulder_path = safe_path_to_initial_point_in_trajectory(1500, triangle_loop(shoulder_path_min, shoulder_path_max, 2))
    elbow_path = safe_path_to_initial_point_in_trajectory(1500, triangle_loop(elbow_path_min, elbow_path_max, 2))
    sleep(1)

    #runs test loop for all selected joints.
    pwm_update_loop(robot, base_path, shoulder_path, elbow_path)
    
    #turn all motors off.
    for motor_id in range(0,5):
        serial_out.update_servo(motor_id, 0)