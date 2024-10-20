from serial import Serial, SerialException
from time import sleep
from typing import List, Collection
from itertools import chain, cycle
from time import time
import os
from SerialJointUpdateInterface import SerialServoPositionUpdater, ServoPositionUpdater


def find_current_motor_position(srrial_port_updater: ServoPositionUpdater, motor_id: int) -> int:
    sleep(0.02)
    srrial_port_updater.serial.write(bytes(f'QP{motor_id} \r', "UTF8")) # sets robot to initial position.
    returned_hex = int.from_bytes(srrial_port_updater.serial.read(1), "big")
    return returned_hex


def find_current_motor_positions(serial_port: Serial, motor_ids: Collection) -> dict:
    """returns the current motor position."""
    output_dict = {motor_id: find_current_motor_position(serial_port, motor_id) for motor_id in motor_ids}
    return output_dict


serial_out = SerialServoPositionUpdater("/dev/tty.usbserial-AB0NBPCE", 115200)
try:
    print("starting test!")
    init_string = b"DEFAULT CONFIG\r" #initialises the string

    current_positions = find_current_motor_positions(serial_out, range(0,6))
    print(current_positions)
    sleep(0.2)
    
    base_rotation_there = iter(range(1500, 1900, 2))
    base_rotation_back = iter(range(1900, 1500, -2))
    base_rotation_cycle = cycle(chain(base_rotation_there, base_rotation_back))

    shoulder_rotation_there = iter(range(1500, 1900, 1))
    shoulder_rotation_back = iter(range(1900, 1500, -1))
    shoulder_rotation_cycle = cycle(chain(shoulder_rotation_there, shoulder_rotation_back))


    elbow_rotation_there = iter(range(1900, 1300, -4))
    elbow_rotation_back = iter(range(1300, 1900, 4))
    elbow_rotation_cycle = cycle(chain(elbow_rotation_there, elbow_rotation_back))

    while True:
        try:
            start_time = time()
            next_location_base = next(base_rotation_cycle)
            next_location_shoulder = next(shoulder_rotation_cycle)
            next_location_elbow = next(elbow_rotation_cycle)
            
            serial_out.update_servo(0, next_location_base)
            serial_out.update_servo(1, next_location_shoulder)
            serial_out.update_servo(2, next_location_elbow)

            end_time = time()
            total_time_elapsed = end_time - start_time
            percentage_of_loop = total_time_elapsed*100/0.01 #used to make sure we arent doing too many calculations.
            sleep(0.01) #sleeps, think of this like an interrupt.
        except GeneratorExit:
            break
    print("exited_loop")
except KeyboardInterrupt:
    print("PROCESS FINISHED!")
    #turn all motors off.
    for motor_id in range(0,5):
        serial_out.update_servo(motor_id, 0)