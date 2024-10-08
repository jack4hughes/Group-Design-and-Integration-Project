from config_scripts import load_config_file_from_yaml

class ServoMotor:
    def __init__(self, pwm_pin = None, name=None, config_dict=None):
        if config_dict == None:
            pass
        else:
            if name == None:
                self.servo_name = config_dict["servo_name"]
            else:
                self.servo_name = name

            if pwm_pin == None:
                self.pwm_pin = config_dict["pin_out"]
            else:
                self.pwm_pin = pwm_pin

            self.range_of_movement = config_dict["degrees_of_movement"]
            
            self.duty_cycle_ms = config_dict["duty_cyle_ms"]
            self.max_angle_duty_cycle_ms = config_dict["max_angle_duty_cycle_ms"]
            self.min_angle_duty_cycle_ms = config_dict["min_angle_duty_cycle_ms"]

            self.max_degree_value = config_dict["max_degree_value"] 
            self.min_degree_value = config_dict["min_degree_value"]

            self.torque = config_dict["torque"]
            self.volts = config_dict["volts"]

    def update_position(new_position_pwm_value):
        """Updates the position of our servo based directly off of PWM values. This is how we actually move the motors."""
        pass


def create_servo_object_from_config_file(config_file_location: str) -> dict:
    servo_config_dict = load_config_file_from_yaml(config_file_location)
    return ServoMotor(
        pwm_pin=servo_config_dict["pin_out"], 
        config_dict=servo_config_dict)

if __name__ == "__main__":
    test_servo_config_file_location = "Motor Config Files/servo_1_config.yaml"
    test_servo =create_servo_object_from_config_file(test_servo_config_file_location)