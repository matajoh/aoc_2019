import sys
from collections import namedtuple

import pytest

from common import a_star, asset, read_tests


class Vector(namedtuple("Vector", ["x", "y"])):
    """ 2D Vector """

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def neighbors(self):
        """ The cardinal neighbors of this vector """
        return [self + move for move in Directions]

    @property
    def length(self):
        """ L1 length of the vector """
        return abs(self.x) + abs(self.y)


Directions = [
    Vector(0, -1),
    Vector(0, 1),
    Vector(-1, 0),
    Vector(1, 0)
]


class ActionOrder(namedtuple("ActionOrder", ["keys", "keys_set", "steps", "location"])):  
    def add(self, key, steps, location):
        return ActionOrder(self.keys + [key], self.keys_set | {key}, self.steps + steps, location)
    
    @property
    def obtained(self):
        return "".join(sorted(self.keys))
    
    def __contains__(self, key):
        return key in self.keys_set
    
    def __lt__(self, other):
        return self.steps < other.steps
    
    def __repr__(self):
        return ", ".join([item for item in self.keys if item.islower()])


class Cave:
    def __init__(self, lines):
        self.open = set()
        self.entrance = None
        self.walls = set()
        self.keys = set()
        self.doors = set()
        self.item_loc = {}
        self.loc_item = {}
        self.path_steps = {}
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                loc = Vector(x, y)
                if char == '#':
                    self.walls.add(loc)
                elif char == '.':
                    self.open.add(loc)
                elif char == '@':
                    self.entrance = loc
                    self.open.add(loc)
                elif char.isalpha():
                    if char.islower():
                        self.keys.add(loc)
                    else:
                        self.doors.add(loc)
                    
                    self.item_loc[char] = loc
                    self.loc_item[loc] = char
                else:
                    raise ValueError("Unexpected character: " + char)
    
    def find_steps(self, order, key):
        start = order.location
        nodes = {self.item_loc[key] for key in order.keys}
        nodes |= {self.item_loc[key.upper()] for key in order.keys if key.upper() in self.item_loc}
        lookup = (start, order.obtained, key)
        if lookup not in self.path_steps:
            goal = self.item_loc[key]
            nodes = self.open | nodes | {goal}
            path = a_star(start, goal, nodes)
            self.path_steps[lookup] = None if path is None else len(path) - 1
        
        return self.path_steps[lookup]    


    def find_keys(self):
        min_steps = sys.maxsize
        min_order = None
        orders = [ActionOrder([], set(), 0, self.entrance)]
        while orders:
            order = orders.pop()
            if len(order.keys) == len(self.keys):
                if order.steps < min_steps:
                    min_steps = order.steps
                    min_order = order
                    print(min_steps, min_order)

                continue

            to_add = []
            for goal in self.keys:
                key = self.loc_item[goal]
                if key in order:
                    continue

                steps = self.find_steps(order, key)
                if steps is not None and steps < min_steps:
                    to_add.append(order.add(key, steps, goal))
            
            if to_add:
                to_add.sort(key=lambda order: order.steps, reverse=True)
                orders.extend(to_add)

        return min_order

@pytest.fixture(scope="module")
def tests():
    return read_tests("day18_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, 8),
    (1, 86),
    (2, 132),
    (3, 136),
    (4, 81)
])
def test_find_key(tests, index, expected):
    cave = Cave(tests[index])
    action_list = cave.find_keys()
    assert action_list.steps == expected


def _main():
    with open(asset("day18.txt")) as file:
        #cave = Cave(file)
        cave = Cave(read_tests("day18_tests.txt")[3])
    
    action_list = cave.find_keys()
    print("Part 1:", action_list.steps)


if __name__ == "__main__":
    _main()
