"""A collection of functions that generate paths for our robots"""

from itertools import cycle, chain
from Robot import Robot
from typing import Iterable

def lerp_path_generator(min_value: int, max_value: int, step_length: int):
    """Linearly moves from one value to the next."""
    step_values = iter(range(min_value, max_value, step_length))
    return step_values


def triangle_loop(min_value, max_value, step_length):
    """Loops from one angle to another in a triangular way. (IE linear there, linear back)"""
    path_there = range(min_value, max_value, step_length))
    path_back = iter(range(max_value, min_value, -step_length))
    rotation_cycle = cycle(chain(path_there, path_back))

    return rotation_cycle


def safe_path_to_initial_point_in_trajectory(initial_value: int, path_iterator: Iterable):
    """Allows us to safely move to the starting point of our animation by LERPing to its initial value."""
    first_point = next(path_iterator)
    if first_point - initial_value == 0:
        return path_iterator
    elif first_point - initial_value > 0:
        step_length = 1
    elif first_point -  initial_value < 0:
        step_length = -1

    initial_path = lerp_path_generator(initial_value, first_point, step_length)
    output = chain(initial_path, path_iterator)

    return output
