""" Solution for day 15 """

from collections import namedtuple
from enum import IntEnum

import numpy as np

from intcode import Computer
from common import asset, a_star, Vector, Neighbors

import glasskey as gk


Directions = [
    Vector(0, -1),
    Vector(0, 1),
    Vector(-1, 0),
    Vector(1, 0)
]

def _to_command(vec):
    return Directions.index(vec) + 1


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
        return len(a_star(start, goal, Neighbors(self.empty))) - 1

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
            loc = locs.pop()
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
            locs.extend(loc.neighbors())

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
        return a_star(start, goal, Neighbors(self._empty | {location}))

    def move_to(self, location):
        """ Move to the specified location """
        if (location - self.location).length == 1:
            commands = [_to_command(location - self.location)]
        else:
            path = self.find_shortest_path(location)
            commands = [_to_command(pos1 - pos0) for pos0,
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
    sector = robot.explore()
    sector.draw()
    print("Part 1:", sector.steps_to_oxygen())
    print("Part 2:", sector.fill())

    #_explore_animation(program, sector)
    # _fill_animation(sector)


if __name__ == "__main__":
    _main()
