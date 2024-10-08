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
    pprint.pprint(robot_config_file)

def link_joints_from_config_file(config_file_location):
    """returns a dict of Joint objects that have been specified in a config file, in the order they appear in on the robot. each joint carries a name (even if its joint1 etc.)"""
    pass

if __name__ == "__main__":
    load_joint_configs_from_config_file(config_file_location)
