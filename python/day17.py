import sys
from collections import namedtuple
from typing import Set
from io import StringIO

from intcode import Computer
from common import asset


class Vector(namedtuple("Vector", ["x", "y"])):
    """ 2D Vector """

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def find_neighbors(self) -> Set["Vector"]:
        """ The cardinal neighbors of this vector """
        return {self + move for move in DIRECTIONS}
    
    def is_intersection(self, scaffolds):
        neighbors = self.find_neighbors()
        return len(neighbors & scaffolds) == 4

    @property
    def alignment_parameter(self):
        """ L1 length of the vector """
        return self.x*self.y
    

    @property
    def length(self):
        return abs(self.x) + abs(self.y)
    
    @property
    def direction(self):
        assert self.x == 0 or self.y == 0
        norm = Vector(-1 if self.x < 0 else (1 if self.x > 0 else 0),
                      -1 if self.y < 0 else (1 if self.y > 0 else 0))
        return DIRECTIONS.index(norm)


DIRECTIONS = [
    Vector(0, -1),
    Vector(1, 0),
    Vector(0, 1),
    Vector(-1, 0)
]

ROBOT = "^>v<"


class Robot:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.commands = []

    def valid_move(self, scaffolds):
        left = (self.direction - 1)%4
        right = (self.direction + 1)%4
        left = self.position + DIRECTIONS[left]
        right = self.position + DIRECTIONS[right]
        if left in scaffolds:
            return left - self.position
        
        if right in scaffolds:
            return right - self.position
        
        return None
    
    def add_segment(self, vector):
        direction = vector.direction
        if direction == (self.direction - 1)%4:
            self.commands.append("L")
        elif direction == (self.direction + 1)%4:
            self.commands.append("R")
        else:
            raise AssertionError("Invalid direction")
            
        self.direction = direction
        self.position += vector
        self.commands.append(str(vector.length))



def _parse_scaffolds(text):
    lines = text.split('\n')
    scaffolds = set()
    robot = None
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != '.':
                scaffolds.add(Vector(x, y))
            
            if char in ROBOT:
                robot = Robot(Vector(x, y), ROBOT.index(char))

    return scaffolds, robot


def _find_intersections(scaffolds):
    return [scaffold
            for scaffold in scaffolds
            if scaffold.is_intersection(scaffolds)]


def _sum_of_alignment_parameters(scaffolds):
    return sum([intersection.alignment_parameter
                for intersection in _find_intersections(scaffolds)])


def _follow_scaffolds(scaffolds, robot):
    num_scaffolds = len(scaffolds)
    start = robot.position
    end = start
    direction = robot.valid_move(scaffolds)
    visited = set([start])
    while len(visited) < num_scaffolds:
        loc = end + direction
        if end in scaffolds:
            visited.add(loc)
            end = loc
        else:
            robot.add_segment(end - start)
            start = end
            direction = robot.valid_move(scaffolds)
            if direction is None:
                break

    if start != end:
        robot.add_segment(end - start)


TEST = """..#..........
..#..........
#######...###
#.#...#...#.#
#############
..#...#...#..
..#####...^..
"""


def test_sum_alignment_params():
    scaffolds, _ = _parse_scaffolds(TEST)
    assert _sum_of_alignment_parameters(scaffolds) == 76


def _ascii(program):
    computer = Computer(program)

    last = None
    output = StringIO()
    while not computer.is_halted:
        while not computer.num_outputs:
            computer.step()
        
        tile = chr(computer.read())
        if last == tile == '\n':
            break

        last = tile
        output.write(tile)
        sys.stdout.write(tile)
    
    return output.getvalue()

def _main():
    with open(asset("day17.txt")) as file:
        program = [int(part) for part in file.read().split(',')]
    
    text = _ascii(program)

    scaffolds, robot = _parse_scaffolds(text)
    print("Part 1:", _sum_of_alignment_parameters(scaffolds))

    _follow_scaffolds(scaffolds, robot)
    print(robot.commands)



if __name__ == "__main__":
    _main()
