import numpy as np
import yaml

def create_position_vector(x,y,z):
    return np.array([[x],[y],[z],[1]])

#
def create_matrix_from_dh_values(joint_angle = 0, joint_distance = 0, link_twist_angle = 0, common_normal_length = 0):
    """used https://lavalle.pl/planning/node111.html to create a Homogenous Transform Matrix from a DH table, provided as a dict or as raw numbers."""
    if type(joint_angle) == dict:
        return create_matrix_from_dh_values(**joint_angle) #allows dict to be passed straight in, function handles unpacking

    joint_angle_radians = np.radians(joint_angle)
    link_twist_angle_radians = np.radians(link_twist_angle)
    
    cos_joint_angle = np.cos(joint_angle_radians)
    sin_joint_angle = np.sin(joint_angle_radians)

    cos_link_twist_angle = np.cos(link_twist_angle_radians)
    sin_link_twist_angle = np.sin(link_twist_angle_radians)

    rotation_matrix = np.array([
                        (cos_joint_angle, -sin_joint_angle, 0, common_normal_length), 
                        (cos_link_twist_angle*sin_joint_angle, cos_joint_angle*cos_link_twist_angle, -sin_link_twist_angle, -sin_link_twist_angle*joint_distance), 
                        (sin_joint_angle*sin_link_twist_angle, cos_joint_angle*sin_link_twist_angle, cos_link_twist_angle, cos_link_twist_angle*joint_distance),
                        (0,0,0,1)
                        ])

    return rotation_matrix


def get_pose_from_transform_matrix():
    pass


def rotate_matrix_around_x_axis(input_matrix, rotation_radians: float):
    rotation_matrix = np.array([[1, 0, 0, 0],
                                [0, np.cos(rotation_radians), -np.sin(rotation_radians), 0],
                                [0, np.sin(rotation_radians), np.cos(rotation_radians), 0],
                                [0, 0, 0, 1]
                                ])
    
    return input_matrix @ rotation_matrix


def rotate_matrix_around_y_axis(input_matrix, rotation_radians: float):
    rotation_matrix = np.array([np.cos(rotation_radians),0,np.sin(rotation_radians),0],
                               [0,1,0,0],
                               [-np.sin(rotation_radians),0,np.cos(rotation_radians),0],
                               [0,0,0,1]) 
      
    return input_matrix @ rotation_matrix


def rotate_matrix_around_z_axis(input_matrix, rotation_radians: float):
    rotation_matrix = np.array([np.cos(rotation_radians),-np.sin(rotation_radians),0,0],
                               [np.sin(rotation_radians),np.cos(rotation_radians),0,0],
                               [0,0,1,0],
                               [0,0,0,1]) 
    
    return input_matrix @ rotation_matrix


def rotate_matrix_around_axis(input_matrix: np.array, rotation_radians: float, axis: str):
    if axis == "x":
        return rotate_matrix_around_x_axis(input_matrix, rotation_radians)

    if axis == "y":
        return rotate_matrix_around_y_axis(input_matrix, rotation_radians)

    if axis == "z":
        return rotate_matrix_around_z_axis(input_matrix, rotation_radians)
    else:
        raise ValueError("Incorrect rotation axis, rotation axis must be a string of single character: x, y or z")


with open("Motor Config Files/robot_setup_config.yaml") as file:
    joint_data = yaml.safe_load(file)

homogenous_transform_matricies = [create_matrix_from_dh_values(joint["initial_dh_dict"]) for joint in joint_data]

for matrix in homogenous_transform_matricies:
    print(matrix)
