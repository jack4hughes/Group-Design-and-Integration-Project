"""A collection of functions that generate paths for our robots"""
import datetime
from itertools import cycle, chain
from Robot import Robot
from typing import Iterable
import numpy as np
from typing import Union, Collection
from more_itertools import windowed   #https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.windowed


def joint_space_lerp(initial_joint_pose: Union[list, np.array], final_joint_pose, time, updates_per_second):
    updates_until_completion = int(time*updates_per_second)
    position_matrix = np.linspace(initial_joint_pose, final_joint_pose, updates_until_completion, dtype=int)
    return position_matrix


def lerp_between_list_of_joints(list_of_joint_poses: Collection[np.array], time_to_next_joint: Collection[float], updates_per_second):
    """Lerps between adjacent joints provided in a list of joint poses. Lerps between angle values with no IK"""
    final_list_of_lerps = []
    windowed_list = windowed(list_of_joint_poses, 2)
    windowed_list = zip(windowed_list, time_to_next_joint)
    for item in windowed_list:
        print(item[0][0])
        print(item[0][1])
        print("____")
        lerp = joint_space_lerp(item[0][0], item[0][1], item[1], updates_per_second)
        final_list_of_lerps.append(lerp) # According to this collecting these in a list is more efficient than multiple np.concatenate. https://stackoverflow.com/questions/38470264/numpy-concatenate-is-slow-any-alternative-approach

    return np.concatenate(final_list_of_lerps)


if __name__ == "__main__":
    intial_joint_loc = np.array([500, 500, 500, 500, 500])
    second_joint_loc = np.array([2500, 1000, 550, 350, 2500])
    final_joint_loc = np.array([1500, 1500, 1500, 1500, 1650])

    lerp_path = joint_space_lerp(intial_joint_loc, final_joint_loc, 3, 50)
    lerp_iterator = iter(lerp_path)

    lerps = lerp_between_list_of_joints([intial_joint_loc, second_joint_loc, final_joint_loc, intial_joint_loc], [2,3,1,2], 50)
    print(lerps.shape)