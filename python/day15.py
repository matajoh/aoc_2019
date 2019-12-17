""" Solution for day 15 """

import sys
import os

from collections import namedtuple
from typing import Iterable
from enum import IntEnum
import heapq

import numpy as np

from intcode import Computer
from common import asset

import glasskey as gk


class Vector(namedtuple("Vector", ["x", "y"])):
    """ 2D Vector """

    @property
    def command(self):
        """ The command needed to move in a direction """
        return Directions.index(self) + 1

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def neighbors(self) -> Iterable["Vector"]:
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


def distance(lhs: Vector, rhs: Vector) -> int:
    """ Compute the L1 distance between two vectors """
    return (rhs - lhs).length


def reconstruct_path(came_from, current):
    """ Reconsruct the optimal path """
    total_path = [current]

    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    total_path.reverse()
    return total_path


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

    raise ValueError("No path found from {} to {}".format(start, goal))


class Status(IntEnum):
    """ The robot status """
    Wall = 0
    Empty = 1
    OxygenSystem = 2


def _to_numpy(vectors):
    result = np.zeros((len(vectors), 2), np.int32)
    for i, vector in enumerate(vectors):
        result[i, 0] = vector.x
        result[i, 1] = vector.y

    return result


class Sector(namedtuple("Sector", ["walls", "empty", "oxygen_system"])):
    """ Class representing the sector in which the robot exists """

    def save(self, file):
        """ Saves the sector information to file """
        walls = _to_numpy(self.walls)
        empty = _to_numpy(self.empty)
        oxygen_system = np.array(self.oxygen_system, np.int32)
        np.savez(file, walls=walls, empty=empty,
                 oxygen_system=oxygen_system)

    def bounds(self):
        """ The bounds of the sector """
        max_x = max([loc.x for loc in self.walls])
        max_y = max([loc.y for loc in self.walls])
        min_x = min([loc.x for loc in self.walls])
        min_y = min([loc.y for loc in self.walls])

        width = max_x - min_x + 1
        height = max_y - min_y + 1
        return gk.Rect(min_x, min_y, width, height)

    @staticmethod
    def load(file):
        """ Loads the sector information from file """
        data = np.load(file)
        walls = [Vector(*loc) for loc in data["walls"]]
        empty = [Vector(*loc) for loc in data["empty"]]
        oxygen_system = Vector(*data["oxygen_system"])
        return Sector(walls, empty, oxygen_system)

    def fill(self, step_cb=None):
        """ Fill the sector with oxygen """
        frontier = [(0, self.oxygen_system)]

        oxygen = set()
        max_minutes = 0
        while frontier:
            minute, loc = frontier.pop(0)
            if loc in self.walls or loc in oxygen:
                continue

            oxygen.add(loc)
            max_minutes = max(max_minutes, minute)
            frontier.extend([(minute+1, neighbor)
                             for neighbor in loc.neighbors()])

            if step_cb:
                step_cb(self.walls, self.empty, oxygen)

        return max_minutes

    def steps_to_oxygen(self):
        """ Compute the number of steps to get to the oxygen
            system from the origin. """
        start = Vector(0, 0)
        goal = self.oxygen_system
        nodes = self.empty
        return len(a_star(start, goal, nodes)) - 1

    def draw(self, drone=Vector(0, 0)):
        """ Draw the sector to the console """
        bounds = self.bounds()

        offset = Vector(bounds.left, bounds.top)
        lines = [['.']*bounds.width for _ in range(bounds.height)]
        for wall in self.walls:
            pos = wall - offset
            lines[pos.y][pos.x] = '#'

        pos = self.oxygen_system - offset
        lines[pos.y][pos.x] = 'O'
        pos = drone - offset
        lines[pos.y][pos.x] = 'D'
        for line in lines:
            print("".join(line))


class RepairDrone:
    """ Represents the repair drone """
    def __init__(self, program, move_cb=None):
        self._cpu = Computer(program)
        self.location = Vector(0, 0)
        self._empty = set()
        self._walls = set()
        self._oxygen_system = None
        self._move_cb = move_cb

    def explore(self):
        """ Explore the sector.

        Returns:
            a sector map
        """
        locs = [self.location]
        iteration = 0
        self._walls = set()
        self._empty = set()
        self._oxygen_system = None
        while locs:
            loc = locs.pop(0)
            iteration += 1
            if loc in self._walls or loc in self._empty:
                continue

            if iteration % 100 == 0:
                print("robot at", loc, len(locs), len(self._walls))

            status = self.move_to(loc)
            if status == Status.Wall:
                self._walls.add(loc)
                continue

            assert self.location == loc
            if status == Status.OxygenSystem:
                print(loc, "is the oxygen system")
                self._oxygen_system = loc

            self._empty.add(loc)
            locs = loc.neighbors() + locs

        return Sector(self._walls, self._empty, self._oxygen_system)

    def move(self, direction):
        """ Move the drone in the specified direction """
        self.location += direction
        if self._move_cb:
            self._move_cb(self.location, self._walls,
                          self._empty, self._oxygen_system)

    def find_shortest_path(self, location):
        """ Find the shortest path to a location """
        start = self.location
        goal = location
        nodes = list(self._empty) + [location]
        return a_star(start, goal, nodes)

    def move_to(self, location):
        """ Move to the specified location """
        if (location - self.location).length == 1:
            commands = [(location - self.location).command]
        else:
            path = self.find_shortest_path(location)
            commands = [(pos1 - pos0).command for pos0,
                        pos1 in zip(path[:-1], path[1:])]

        status = Status.Empty
        for command in commands:
            while not self._cpu.needs_input:
                self._cpu.step()

            self._cpu.write(command)
            while not self._cpu.num_outputs:
                self._cpu.step()

            status = self._cpu.read()
            if status != Status.Wall:
                self.move(Directions[command-1])

        return Status(status)


def _explore_animation(program, sector):
    bounds = sector.bounds()
    gk.start()
    grid = gk.create_grid(bounds.height, bounds.width, "Repair Droid")
    grid.map_color('#', gk.Colors.Red)
    grid.map_color('D', gk.Colors.White)
    grid.map_color('.', gk.Colors.Gray)
    grid.map_color('O', gk.Colors.Blue)
    offset = Vector(bounds.left, bounds.top)

    def _move_cb(location, walls, empty, oxygen_system):
        for tile in walls:
            pos = tile - offset
            grid.draw(pos.y, pos.x, "#")

        for tile in empty:
            pos = tile - offset
            grid.draw(pos.y, pos.x, '.')

        if oxygen_system:
            pos = oxygen_system - offset
            grid.draw(pos.y, pos.x, 'O')

        pos = location - offset
        grid.draw(pos.y, pos.x, "D")

        grid.blit()
        gk.next_frame(30)

    input("Press enter to start animation...")
    robot = RepairDrone(program, move_cb=_move_cb)
    robot.explore()
    gk.stop()


def _fill_animation(sector):
    bounds = sector.bounds()
    gk.start()
    grid = gk.create_grid(bounds.height, bounds.width, "Oxygen Fill")
    grid.map_color('#', gk.Colors.Red)
    grid.map_color('.', gk.Colors.Gray)
    grid.map_color('O', gk.Colors.Blue)
    offset = Vector(bounds.left, bounds.top)

    def _step_cb(walls, empty, oxygen):
        for tile in walls:
            pos = tile - offset
            grid.draw(pos.y, pos.x, "#")

        for tile in empty:
            pos = tile - offset
            grid.draw(pos.y, pos.x, '.')

        for tile in oxygen:
            pos = tile - offset
            grid.draw(pos.y, pos.x, 'O')

        grid.blit()
        gk.next_frame(30)

    input("Press enter to start animation...")
    sector.fill(step_cb=_step_cb)
    gk.stop()


def _main():
    with open(asset("day15.txt")) as file:
        program = [int(code) for code in file.read().split(',')]

    robot = RepairDrone(program)
    if os.path.exists("sector.npz"):
        sector = Sector.load("sector.npz")
    else:
        sector = robot.explore()
        sector.save("sector.npz")

    sector.draw()
    print("Part 1:", sector.steps_to_oxygen())
    print("Part 2:", sector.fill())

    #_explore_animation(program, sector)
    # _fill_animation(sector)


if __name__ == "__main__":
    _main()
