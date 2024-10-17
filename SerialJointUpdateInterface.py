from serial import Serial

class SerialJointUpdateInterface:
    """class that opens serial port to send update information directly to SSC 32U chip"""
    def __init__(self, port = None, baudrate: int = 115200):        
        self.serial = Serial(port = port,
                       baudrate = baudrate)
    
    def update_joint(self, joint_id, updated_pwm):
        """sends a message to update the joint position through the serial interface."""
        joint_string_unicode = f"# {joint_id} P {updated_pwm}\r"
        joint_string_bytes = bytes(joint_string_unicode, 'utf8')
        self.serial.write(joint_string_bytes)