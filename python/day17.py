""" Solution to day 17 """

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
        """ Tests if this scaffold is an intersection """
        neighbors = self.find_neighbors()
        return len(neighbors & scaffolds) == 4

    @property
    def alignment_parameter(self):
        """ Used for verification """
        return self.x*self.y

    @property
    def length(self):
        """ The L1 length of the vector """
        return abs(self.x) + abs(self.y)

    @property
    def direction(self):
        """ The direction of the vector """
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
    """ Represents the vacuum robot """

    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.commands = []

    def valid_move(self, scaffolds):
        """ Returns the valid move from the current location """
        left = (self.direction - 1) % 4
        right = (self.direction + 1) % 4
        left = self.position + DIRECTIONS[left]
        right = self.position + DIRECTIONS[right]
        if left in scaffolds:
            return left - self.position

        if right in scaffolds:
            return right - self.position

        return None

    def add_segment(self, vector):
        """ Adds a segment to the robots path """
        direction = vector.direction
        if direction == (self.direction - 1) % 4:
            self.commands.append("L")
        elif direction == (self.direction + 1) % 4:
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
        if loc in scaffolds:
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


def _to_routine_list(text):
    parts = text.split(',')
    routine = []
    for part in parts:
        if part in ('R', 'L'):
            routine.append(part)
        else:
            routine.extend(['1']*int(part))

    return " ".join(routine)


def _to_routine_text(routine):
    parts = routine.split()
    text = []
    count = 0
    for part in parts:
        if part in ('R', 'L', 'A', 'B', 'C'):
            if count:
                text.append(str(count))
                count = 0

            text.append(part)
        else:
            count += 1

    if count:
        text.append(str(count))

    return ",".join(text)


def _replace_subroutine(routine, sub_a, sub_b=None, sub_c=None):
    routine = _to_routine_list(routine)
    routine = routine.replace(_to_routine_list(sub_a), "A")
    if sub_b:
        routine = routine.replace(_to_routine_list(sub_b), "B")

    if sub_c:
        routine = routine.replace(_to_routine_list(sub_c), "C")

    return _to_routine_text(routine)


def _principal_period(s):
    i = (s+s).find(s, 1, -1)
    return None if i == -1 else s[:i]


def _find_subroutines(routine):
    routine = _to_routine_list(routine) + " "
    parts = routine.split()
    max_length = len(parts) // 2
    for i in range(4, max_length):
        sub_a = " ".join(parts[:i]) + " "
        if routine.find(sub_a) == routine.rfind(sub_a):
            break

        routine_a = routine.replace(sub_a, "")
        for j in range(4, max_length):
            sub_b = " ".join(parts[-j:]) + " "
            if routine.find(sub_b) == routine.rfind(sub_b):
                break

            routine_ab = routine_a.replace(sub_b, "")
            sub_c = _principal_period(routine_ab)
            if sub_c:
                routine_abc = routine.replace(sub_a, "A ")
                routine_abc = routine_abc.replace(sub_b, "B ")
                routine_abc = routine_abc.replace(sub_c, "C ")
                routine_abc = routine_abc.strip().replace(' ', ',') + '\n'
                if len(routine_abc) <= 20:
                    sub_a = _to_routine_text(sub_a) + '\n'
                    sub_b = _to_routine_text(sub_b) + '\n'
                    sub_c = _to_routine_text(sub_c) + '\n'
                    return routine_abc, sub_a, sub_b, sub_c

    return None


def _run_routine(program, routine, sub_a, sub_b, sub_c):
    program[0] = 2
    computer = Computer(program)

    while not computer.needs_input:
        computer.step()

    for char in routine + sub_a + sub_b + sub_c + "n\n":
        computer.write(ord(char))

    val = None
    while not computer.is_halted:
        while not computer.num_outputs:
            computer.step()

        val = computer.read()
        if val < 255:
            sys.stdout.write(chr(val))

    return val


TEST = """..#..........
..#..........
#######...###
#.#...#...#.#
#############
..#...#...#..
..#####...^..
"""


def test_sum_alignment_params():
    """ Test """
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
    routine = ",".join(robot.commands)

    routine, sub_a, sub_b, sub_c = _find_subroutines(routine)
    print("Part 2:", _run_routine(program, routine, sub_a, sub_b, sub_c))


if __name__ == "__main__":
    _main()
