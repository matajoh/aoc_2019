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


class ActionOrder(namedtuple("ActionOrder", ["order", "steps", "location"])):  
    def add(self, item, steps, location):
        return ActionOrder(self.order + [item], self.steps + steps, location)
    
    def __contains__(self, item):
        return item in self.order
    
    def __lt__(self, other):
        return self.steps < other.steps
    
    def __repr__(self):
        return ", ".join([item for item in self.order if item.islower()])


class Cave:
    def __init__(self, lines):
        self.open = set()
        self.entrance = None
        self.walls = set()
        self.items = {}
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
                    self.items[char] = loc
                else:
                    raise ValueError("Unexpected character: " + char)
    
    def find_steps(self, action_list, item):
        start = action_list.location
        nodes = {self.items[item] for item in action_list.order}
        key = (start, tuple(nodes), item)
        if key not in self.path_steps:
            goal = self.items[item]
            nodes = self.open | nodes | {goal}
            path = a_star(start, goal, nodes)
            self.path_steps[key] = None if path is None else len(path) - 1
        
        return self.path_steps[key]    


    def find_keys(self):
        complete = []
        action_lists = [ActionOrder([], 0, self.entrance)]
        while action_lists:
            action_list = action_lists.pop()
            if len(action_list.order) == len(self.items):
                complete.append(action_list)
                continue

            for item, goal in self.items.items():
                if item in action_list:
                    continue

                if item.isupper() and item.lower() not in action_list:
                    continue

                steps = self.find_steps(action_list, item)
                if steps:
                    action_lists.append(action_list.add(item, steps, self.items[item]))
            
            print(len(action_lists))

        return min(complete)

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
        cave = Cave(file)
    
    action_list = cave.find_keys()
    print("Part 1:", action_list.steps)


if __name__ == "__main__":
    _main()
