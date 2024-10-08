class ServoMotor:
    def __init__(self, pin, config_dict=None):
        if config_dict == None:
            pass
        else:
            self.degrees_of_movement = config_dict["degrees_of_movement"]
            self.duty_cycle_ms = config_dict["duty_cyle_ms"]
            self.max_angle_duty_cycle_ms = config_dict["max_angle_duty_cycle_ms"]
            self.max_degree_value = config_dict["max_degree_value"]
            self.min_angle_duty_cycle_ms = config_dict["min_angle_duty_cycle_ms"]
            self.min_degree_value = config_dict["min_degree_value"]
            self.servo_name = config_dict["servo_name"]
            self.torque = config_dict["torque"]
            self.volts = config_dict["volts"]
            self.pin_out = config_dict["pin_out"]