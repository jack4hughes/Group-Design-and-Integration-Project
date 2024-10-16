from ServoMotor import ServoMotor

from pprint import pprint
from time import time
from Helper import ANGLE_UNITS, TIME_UNITS, DISTANCE_UNITS, CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME
from time import sleep
import os

REFRESH_FREQUENCY = 0.1 #in seconds

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
        finally:
            pass
    return main_loop_wrapper

@loop_until_keyboard_interrupt
def main_loop():
    print(time())

if __name__ == "__main__":
    main_loop()