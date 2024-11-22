from serial import Serial
from ServoMotor import ServoMotor
from pprint import pprint
from time import time
from datetime import datetime, timedelta
from ServoMotor import ANGLE_UNITS, TIME_UNITS, DISTANCE_UNITS, CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME
from time import sleep
import resource
import os
#from GeneratePaths import lerp_path_generator, triangle_loop, safe_path_to_initial_point_in_trajectory
from  Robot import Robot, create_joint_list_from_config_file, create_joint_from_dict
from SerialJointUpdateInterface import SerialServoPositionUpdater, ServoPositionUpdater
from itertools import cycle, chain
from Joint import PrismaticJoint, RevoluteJoint
import config_scripts
from ControllerLogic import XBoxController, find_xbox_controller
import logging
from logging.handlers import RotatingFileHandler

class MotorError(Exception):
    def __init__(self):
        super().__init__()

REFRESH_FREQUENCY = 0.025 #ms so 20 commands per second.

def clear_screen():
    print('\x1b[2J\x1b[H') #code generated by Claude.
    
def loop_until_keyboard_interrupt(func):
    
    def main_loop_wrapper(*args):
        max_millisecs = timedelta.min
        try:
            while True:
                start_time = datetime.now()
                #prints the robots servo angle information.
                func(*args)
                end_time = datetime.now()

                time_delta = end_time - start_time
                milliseconds_taken = time_delta * 1000
                #loop_percentage = milliseconds_taken/REFRESH_FREQUENCY
                print(f"% processing time: {milliseconds_taken}")
                if milliseconds_taken > max_millisecs:
                    max_millisecs = milliseconds_taken
                print(milliseconds_taken.total_seconds()*1000)
                print(max_millisecs.total_seconds()*1000)
                sleep(REFRESH_FREQUENCY)
                print('\x1b[2J\x1b[H') #created by claude.

        except KeyboardInterrupt:
            print("______________________\nprocess terminated")
            raise Exception
        
        except GeneratorExit:
            print("move complete")
            raise Exception
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


@loop_until_keyboard_interrupt
def controller_update_loop(robot: Robot, controller: XBoxController) -> None:
    initial_time = datetime. now()
    if controller.poll_controller():
        controller_output = controller.processed_controller_output()
        robot.update_joints_from_speed_vector(controller_output)

        for joint in range(len(robot.joints)):
            robot.send_joint_update_message(joint)
            
    robot.print_joint_information()

    print(controller)
 

def controller_robot_update_loop(robot: Robot, controller: XBoxController) -> None:
    i = 0
    try:
        while True:
            if i < 10:
                controller.poll_controller()
            else:
                try:  
                    start_time = datetime.now()
                    controller.poll_controller()
                    controller_output = controller.processed_controller_output() #TODO correct processed controller input.
                    processed_controller_output = robot.process_controller_input(controller_output)
                    robot.update_joints_from_speed_vector(processed_controller_output)
                    
                    for joint_id in range(len(robot.joints)):
                        robot.send_joint_update_message(joint_id)
                    
                    robot.print_joint_information()


                    print(controller)
                    end_time = datetime.now()
                    total_time = end_time - start_time
                    print(total_time.microseconds/1000)
                    print(f"resources: kB: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000}")
                    print(processed_controller_output)
                except ValueError:
                    controller.poll_controller()
                i = 0
            i += 1
            if i > 9:
                clear_screen()
            sleep(0.001)
    except GeneratorExit:
        print("process finished")
    except KeyboardInterrupt:
        print("User killed process.")


NORMAL_ROBOT = "/dev/tty.usbserial-AB0NBPCE"
TEST_ROBOT = "/dev/tty.usbserial-AI02LCJE"

if __name__ == "__main__":
    #initialises robot.
    try:
        serial_out = SerialServoPositionUpdater(NORMAL_ROBOT, 115200)
    
    except:
        serial_out = ServoPositionUpdater()
        print("robot couldn't be found! simulating joint movement")
    
    #Load Joint info from YAML config files
    robot_joint_info = create_joint_list_from_config_file("Motor Config Files/robot_setup_config.yaml")

    #create robot object.
    robot = Robot("Vanessa", robot_joint_info, serial_out)

    #create controller object
    controller_info = find_xbox_controller()
    controller = XBoxController(robot, controller_info[0], controller_info[1])

    #robot.servo_angle_updater.update_servo()
    print("robot initialised!")
    for joint in robot.joints:
        print(joint.angle)
    sleep(2)
    for i in range(len(robot.joints)):
        robot.send_joint_update_message(i)
    #runs test loop for all selected joints.
    controller_robot_update_loop(robot, controller)
    
    #turn all motors off.
    for motor_id in range(0,5): 
        serial_out.update_servo(motor_id, 0)