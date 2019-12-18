""" Common utilities for AOC """

import os
import sys
from typing import List
import heapq


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


def reconstruct_path(came_from, current):
    """ Reconsruct the optimal path """
    total_path = [current]

    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    total_path.reverse()
    return total_path


def distance(lhs, rhs) -> int:
    """ Compute the L1 distance between two vectors """
    return (rhs - lhs).length


def a_star(start, goal, nodes):
    """ Implementation of a-star search """
    came_from = {}
    g_score = {start: 0}
    f_score = {start: distance(start, goal)}
    open_set = [(f_score[start], start)]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in current.neighbors():
            if neighbor not in nodes:
                continue

            tentative_g_score = g_score[current] + distance(current, neighbor)
            if tentative_g_score < g_score.get(neighbor, sys.maxsize):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + \
                    distance(neighbor, goal)
                if neighbor not in open_set:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None
