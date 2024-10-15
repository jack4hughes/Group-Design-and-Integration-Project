ANGLE_UNITS = "°"
DISTANCE_UNITS = "cm"
TIME_UNITS = "ns"
CONFIG_FOLDER_LOCATION = "Motor Config Files"
ROBOT_CONFIG_FILE_NAME =  "robot_setup_config.yaml"


def scale_transform(input, input_range: tuple, output_range: tuple):
    """resizes and shifts the input to match the output range."""
    input_range_min, input_range_max = input_range
    output_range_min, output_range_max = output_range

    input_magnitude = input - input_range_min
    input_normalised = input_magnitude / (input_range_max - input_range_min)
    
    output_magnitude = input_normalised * (output_range_max - output_range_min)
    output = output_range_min + output_magnitude

    return output