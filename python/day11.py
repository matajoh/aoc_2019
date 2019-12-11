""" Solution to day 11 """

import os
from collections import namedtuple
from enum import Enum

from intcode import Computer
import glasskey as gk

ICONS = ['^', '>', 'v', '<']

class Direction(Enum):
    """ Class representing different facings of the robot """

    Up = 0
    Right = 1
    Down = 2
    Left = 3

    def widdershins(self):
        """ Turn anti-clockwise """
        return Direction((self.value-1) % len(Direction))

    def sunwise(self):
        """ Turn clockwise """
        return Direction((self.value + 1) % len(Direction))

    @property
    def icon(self):
        """ Return an icon for the direction """
        return ICONS[int(self)]


class Tile(namedtuple("Tile", ["x", "y"])):
    """ Class representing a tile on the outside of the ship """

    def move(self, direction: Direction):
        """ Get the tile position in the given direction """
        if direction == Direction.Up:
            return Tile(self.x, self.y - 1)

        if direction == Direction.Right:
            return Tile(self.x+1, self.y)

        if direction == Direction.Down:
            return Tile(self.x, self.y+1)

        if direction == Direction.Left:
            return Tile(self.x-1, self.y)

        raise ValueError("Unsupported direction: " + direction.name)


BLACK = 0
WHITE = 1


class Robot:
    """ Class representing the emergency hull painting robot """

    def __init__(self, initial_color=BLACK):
        self.position = Tile(0, 0)
        self.direction = Direction.Up
        self.painted = {Tile(0, 0): initial_color}

    def paint(self, color):
        """ Paint a color onto a tile """
        self.painted[self.position] = color

    def move(self, turn):
        """ Turn and move the robot """
        if turn:
            self.direction = self.direction.sunwise()
        else:
            self.direction = self.direction.widdershins()

        self.position = self.position.move(self.direction)

    def camera(self):
        """ Take a photo from the camera """
        if self.position in self.painted:
            return self.painted[self.position]

        return BLACK


def _run_program(robot, program):
    computer = Computer(program)
    computer.write(robot.camera())
    while not computer.is_halted:
        computer.step()
        if computer.num_outputs == 2:
            robot.paint(computer.read())
            robot.move(computer.read())
            computer.write(robot.camera())

def _bounds(robot):
    x_values = set([tile.x for tile in robot.painted])
    y_values = set([tile.y for tile in robot.painted])

    min_x = min(x_values)
    min_y = min(y_values)
    width = max(x_values) - min_x + 1
    height = max(y_values) - min_y + 1

    return gk.Rect(0, 0, width, height)


def _draw(grid, robot):
    grid.clear(_bounds(robot))

    for tile, color in robot.painted.items():
        grid.draw(tile.y, tile.x, '#' if color else '.')

    grid.draw(robot.position.y, robot.position.x, robot.direction.icon)

    grid.blit()

def _run_program_animated(robot, program):
    grid = gk.create_grid(6, 43, "Painting Robot")
    gk.start()

    computer = Computer(program)
    computer.write(robot.camera())
    _draw(grid, robot)
    input("Press enter to begin...")

    while not computer.is_halted:
        computer.step()
        if computer.num_outputs == 2:
            robot.paint(computer.read())
            robot.move(computer.read())
            computer.write(robot.camera())
            _draw(grid, robot)
            gk.next_frame()

    input("Press any key to finish...")
    gk.stop()

def _part1(program):
    robot = Robot()
    _run_program(robot, program)

    print("Part 1:", len(robot.painted))


def _part2(program, animated=False):
    robot = Robot(WHITE)
    if animated:
        _run_program_animated(robot, program)
    else:
        _run_program(robot, program)

    print("Part 2:")

    bounds = _bounds(robot)

    text = [['.'] * bounds.width for _ in range(bounds.height)]

    for tile, color in robot.painted.items():
        text[tile.y][tile.x] = '#' if color else '.'

    for line in text:
        print("".join(line))


def _main():
    with open(os.path.join("..", "inputs", "day11.txt")) as file:
        program = [int(value) for value in file.read().split(',')]

    _part1(program)
    _part2(program)


if __name__ == "__main__":
    _main()
