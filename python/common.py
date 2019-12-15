""" Common utilities for AOC """

import os
from typing import List


def asset(path: str) -> str:
    """ Return the absolution file path to an input asset """
    return os.path.join(os.path.dirname(__file__), "..", "inputs", path)


def compute_gcd(x, y):
    """ Compute the greatest common denominator of two values """
    while y:
        x, y = y, x % y

    return x


def compute_lcm(x, y):
    """ Compute the least common multiple of two values """
    lcm = (x*y)//compute_gcd(x, y)

    return lcm


def read_tests(path: str) -> List[List[str]]:
    """ Read multiple tests from a test asset """
    tests = []
    current = []
    with open(asset(path)) as file:
        for line in file:
            if line == "---\n":
                tests.append(current)
                current = []
            else:
                current.append(line)

    tests.append(current)
    return tests
