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


class Cave:
    def __init__(self, lines):
        self.open = set()
        self.entrance = None
        self.walls = set()
        self.keys = set()
        self.doors = set()
        self.item_loc = {}
        self.loc_item = {}
        self.scores = {}
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
    
    def reachable(self, start, keys):
        nodes = {self.item_loc[key] for key in keys}
        nodes |= {self.item_loc[key.upper()] for key in keys if key.upper() in self.item_loc}
        for goal in self.keys:
            key = self.loc_item[goal]
            if key in keys:
                continue
                
            path = a_star(start, goal, self.open | nodes | {goal})
            if path:
                yield goal, key, len(path) - 1

    def score(self, start, keys):        
        obtained = "".join(sorted(keys))
        lookup = (start, obtained)
        if lookup not in self.scores:
            if len(keys) == len(self.keys):
                return 0

            self.scores[lookup] = min([self.score(goal, {new_key} | keys) + steps
                                      for goal, new_key, steps in self.reachable(start, keys)])
        
        return self.scores[lookup]    

    def find_keys(self):
        return self.score(self.entrance, set())


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
    assert cave.find_keys() == expected


def _main():
    with open(asset("day18.txt")) as file:
        #cave = Cave(file)
        cave = Cave(read_tests("day18_tests.txt")[3])
    
    print("Part 1:", cave.find_keys())


if __name__ == "__main__":
    _main()
