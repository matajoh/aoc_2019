""" Solution to day 17 """

import sys
from collections import namedtuple
from io import StringIO

from intcode import Computer
from common import asset, Vector
import glasskey as gk


class Position(Vector):
    """ 2D position """

    def is_intersection(self, scaffolds):
        """ Tests if this scaffold is an intersection """
        return len(self.neighbors() & scaffolds) == 4

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
        norm = Position(-1 if self.x < 0 else (1 if self.x > 0 else 0),
                        -1 if self.y < 0 else (1 if self.y > 0 else 0))
        return DIRECTIONS.index(norm)


DIRECTIONS = [
    Position(0, -1),
    Position(1, 0),
    Position(0, 1),
    Position(-1, 0)
]

ROBOT = "^>v<"


class Robot:
    """ Represents the vacuum robot """

    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.commands = []
        self.order = []

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

    def add_segment(self, pos):
        """ Adds a segment to the robots path """
        direction = pos.direction
        if direction == (self.direction - 1) % 4:
            self.commands.append("L")
        elif direction == (self.direction + 1) % 4:
            self.commands.append("R")
        else:
            raise AssertionError("Invalid direction")

        self.direction = direction
        self.position += pos
        self.commands.append(str(pos.length))

    def follow_scaffolds(self, scaffolds):
        """ Follow the scaffolds to find the full sequence of commands """
        num_scaffolds = len(scaffolds)
        start = self.position
        end = start
        direction = self.valid_move(scaffolds)
        visited = set([start])
        self.order = [start]
        while len(visited) < num_scaffolds:
            loc = end + direction
            if loc in scaffolds:
                visited.add(loc)
                self.order.append(loc)
                end = loc
            else:
                self.add_segment(end - start)
                self.order.append(end)
                start = end
                direction = self.valid_move(scaffolds)
                if direction is None:
                    break

        if start != end:
            self.add_segment(end - start)


class Routine(namedtuple("Routine", ("main", "sub_a", "sub_b", "sub_c"))):
    """ A vacuum robot movement routine """

    @staticmethod
    def _principal_period(s):
        i = (s+s).find(s, 1, -1)
        return None if i == -1 else s[:i]

    @staticmethod
    def _to_list(commands):
        if isinstance(commands, str):
            commands = commands.split(',')

        routine = []
        for command in commands:
            if command in ('R', 'L'):
                routine.append(command)
            else:
                routine.extend(['1']*int(command))

        return " ".join(routine)

    @staticmethod
    def _to_text(routine):
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

    def _animation_labels(self, robot):
        routine = self._to_list(robot.commands)
        sub_a = self._to_list(self.sub_a)
        sub_b = self._to_list(self.sub_b)
        sub_c = self._to_list(self.sub_c)
        labels = routine.replace(sub_a, " ".join(['A'] * len(sub_a.split())))
        labels = labels.replace(sub_b, " ".join(['B'] * len(sub_b.split())))
        labels = labels.replace(sub_c, " ".join(['C'] * len(sub_c.split())))
        labels = labels.split()
        return list(zip(robot.order, labels))

    @staticmethod
    def create(commands):
        """ Create a movement routine from the raw command list """
        routine = ",".join(commands)
        routine = Routine._to_list(routine) + " "
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
                sub_c = Routine._principal_period(routine_ab)
                if sub_c:
                    main = routine.replace(sub_a, "A ")
                    main = main.replace(sub_b, "B ")
                    main = main.replace(sub_c, "C ")
                    main = main.strip().replace(' ', ',') + '\n'
                    if len(main) <= 20:
                        sub_a = Routine._to_text(sub_a) + '\n'
                        sub_b = Routine._to_text(sub_b) + '\n'
                        sub_c = Routine._to_text(sub_c) + '\n'
                        return Routine(main, sub_a, sub_b, sub_c)

        return None

    def run(self, program):
        """ Run the movement routine on the robot """
        program = program.copy()
        program[0] = 2
        computer = Computer(program)

        while not computer.needs_input:
            computer.step()

        for char in "".join(self) + "n\n":
            computer.write(ord(char))

        val = None
        while not computer.is_halted:
            while not computer.num_outputs:
                computer.step()

            val = computer.read()
            if val < 255:
                sys.stdout.write(chr(val))

        return val

    @staticmethod
    def draw(grid, lines, labels, frame):
        """ Draw the routine as it animates """
        if frame < 0:
            return

        for tile, label in labels[:frame]:
            lines[tile.y][tile.x] = label

        for row, line in enumerate(lines):
            grid.draw(row, 0, "".join(line))

        grid.blit()
        gk.next_frame()

    def animate(self, program, robot):
        """ Animate the routine """
        labels = self._animation_labels(robot)
        program = program.copy()
        program[0] = 2
        computer = Computer(program)

        while not computer.needs_input:
            computer.step()

        for char in "".join(self) + "y\n":
            computer.write(ord(char))

        gk.start()
        rows = 37
        cols = 45
        grid = gk.create_grid(rows, cols, "Vacuum Robot")
        grid.map_color('.', gk.Colors.Navy)
        grid.map_color('#', gk.Colors.Gray)
        grid.map_color('A', gk.Colors.Red)
        grid.map_color('B', gk.Colors.Green)
        grid.map_color('C', gk.Colors.Blue)
        lines = [[' ']*cols for _ in range(rows)]
        row = 0
        col = 0
        frame = -2
        input("Press enter to begin animation...")
        while not computer.is_halted:
            while not computer.num_outputs:
                computer.step()

            val = computer.read()
            if val < 255:
                if val == ord('\n'):
                    if col:
                        row += 1
                        col = 0
                    else:
                        self.draw(grid, lines, labels, frame)
                        row = 0
                        col = 0
                        frame += 1
                else:
                    lines[row][col] = chr(val)
                    col += 1

        self.draw(grid, lines, labels, frame)
        gk.stop()


def _parse_scaffolds(text):
    lines = text.split('\n')
    scaffolds = set()
    robot = None
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != '.':
                scaffolds.add(Position(x, y))

            if char in ROBOT:
                robot = Robot(Position(x, y), ROBOT.index(char))

    return scaffolds, robot


def _find_intersections(scaffolds):
    return [scaffold
            for scaffold in scaffolds
            if scaffold.is_intersection(scaffolds)]


def _sum_of_alignment_parameters(scaffolds):
    return sum([intersection.alignment_parameter
                for intersection in _find_intersections(scaffolds)])


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

    robot.follow_scaffolds(scaffolds)
    routine = Routine.create(robot.commands)
    print("Part 2:", routine.run(program))

    #routine.animate(program, robot)


if __name__ == "__main__":
    _main()
