import os
import yaml
import pprint

CONFIG_FOLDER_LOCATION = "Motor Config Files"
ROBOT_CONFIG_FILE_NAME =  "robot_setup_config.yaml"
config_file_location = os.path.join(CONFIG_FOLDER_LOCATION, ROBOT_CONFIG_FILE_NAME)

    
def load_config_file_from_yaml(location): 
    with open(location) as config:
        yaml_config_dict = yaml.safe_load(config)
        return yaml_config_dict

def load_joint_configs_from_config_file(location):
    robot_config_file = load_config_file_from_yaml(location)
    return robot_config_file


if __name__ == "__main__":
    print("Robot config file\n")
    pprint.pprint(load_joint_configs_from_config_file(config_file_location))
    print("\njoint config file\n")
    pprint.pprint(load_config_file_from_yaml("Motor Config Files/servo_2_config.yaml"))