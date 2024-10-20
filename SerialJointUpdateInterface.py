from serial import Serial
from typing import Union, Dict
try:
    import machine
except ModuleNotFoundError:
    pass

class ServoPositionUpdater:
    """Our base class for joint updates, all methods should be overwritten by our specific joint update
    implementation"""
    def update_servo(self, joint_id, pwm):
        raise NotImplementedError("You need to spefify the type of JointUpdaterInterface you want. if using a computer w/ serial use SerialJointUpdaterInterface, if using Rasberry Pi Pico use ")

    def get_joint_info(self):
        return NotImplementedError("You need to spefify the type of JointUpdaterInterface you want. if using a computer w/ serial use SerialJointUpdaterInterface, if using Rasberry Pi Pico use ")

class SerialServoPositionUpdater(ServoPositionUpdater):
    """class that opens serial port to send update information directly to SSC 32U chip"""
    def __init__(self, port = None, baudrate: int = 115200):        
        self.serial = Serial(port = port,
                       baudrate = baudrate)
    
    def update_servo(self, servo_id, pwm) -> None:
        """sends a message to update the joint position through the serial interface."""
        servo_string_unicode = f"# {servo_id} P {pwm}\r"
        servo_string_bytes = bytes(servo_string_unicode, 'utf8')
        self.serial.write(servo_string_bytes)


    def turn_servo_off(self, servo_id) -> None:
        self.update_servo(servo_id, 0)
    
    
    def get_joint_info(self, joint_id):
        pass


class PiPicoServoPositionUpdater(ServoPositionUpdater):
    def __init__(self, pin_map: Dict[Union[int, str], int]):
        self.pin_map = pin_map

    def update_servo(self, joint_id, pwm):
        """Updates PWM values on the correct servos' PWM pin, moving servo directly."""
        #TODO: implement on rasberry pi pico.
        pass

    def get_joint_info(self):
        #TODO: implement on rasberry pi pico.
        return None
    