""" Common utilities for AOC """

import os
import sys
from collections import namedtuple
from functools import lru_cache, reduce
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


class Vector(namedtuple("Vector", ["x", "y"])):
    """ 2D Vector """

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self.__class__(self.x - other.x, self.y - other.y)

    @lru_cache(maxsize=None)
    def neighbors(self):
        """ The cardinal neighbors of this vector """
        return {
            self.__class__(self.x, self.y - 1),
            self.__class__(self.x, self.y + 1),
            self.__class__(self.x - 1, self.y),
            self.__class__(self.x + 1, self.y)
        }

    @property
    def length(self):
        """ L1 length of the vector """
        return abs(self.x) + abs(self.y)


class Neighbors:
    """ Callable which only returns valid neighbors """
    def __init__(self, valid):
        self._valid = valid

    def __call__(self, vec):
        return vec.neighbors() & self._valid


def a_star(start, goal, neighbors, distance=None, heuristic=None):
    """ Implementation of a-star search """

    if distance is None:
        distance = lambda lhs, rhs: 1

    if heuristic is None:
        heuristic = lambda lhs, rhs: (lhs - rhs).length

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    open_set = [(f_score[start], start)]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in neighbors(current):
            tentative_g_score = g_score[current] + distance(current, neighbor)
            if tentative_g_score < g_score.get(neighbor, sys.maxsize):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + \
                    heuristic(neighbor, goal)
                if neighbor not in open_set:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None


def ExtendedEuclideanAlgorithm(a, b):
    """
        Calculates gcd(a,b) and a linear combination such that
        gcd(a,b) = a*x + b*y

        As a side effect:
        If gcd(a,b) = 1 = a*x + b*y
        Then x is multiplicative inverse of a modulo b.
    """
    aO, bO = a, b

    x=lasty=0
    y=lastx=1
    while (b!=0):
        q= a//b
        a, b = b, a%b
        x, lastx = lastx-q*x, x
        y, lasty = lasty-q*y, y

    return {
        "x": lastx,
        "y": lasty,
        "gcd": aO * lastx + bO * lasty
    }

def solveLinearCongruenceEquations(rests, modulos):
    """
    Solve a system of linear congruences.

    >>> solveLinearCongruenceEquations([4, 12, 14], [19, 37, 43])
    {'congruence class': 22804, 'modulo': 30229}
    """
    assert len(rests) == len(modulos)
    x = 0
    M = reduce(lambda x, y: x*y, modulos)

    for mi, resti in zip(modulos, rests):
        Mi = M // mi
        s = ExtendedEuclideanAlgorithm(Mi, mi)["x"]
        e = s * Mi
        x += resti * e
    return {"congruence class": ((x % M) + M) % M, "modulo": M}