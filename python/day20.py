""" Solution to day 20 """

import pytest

from common import Vector, a_star, read_tests, asset

#pylint: disable=redefined-outer-name


class DonutMaze:
    """ Class representing a Plutonian donut maze """

    def __init__(self, lines):
        self.walls = set()
        self.open = set()
        portals = {}
        self.portals = {}
        self.warps = {}
        self.inner_warps = set()
        self.outer_warps = set()
        self.warp_portal = {}
        self.rows = len(lines)
        self.cols = len(lines[0]) - 1
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                loc = Vector(x, y)
                if char == '#':
                    self.walls.add(loc)
                elif char == '.':
                    self.open.add(loc)
                elif char.isalpha():
                    portals[loc] = char

        self._init_portals(portals)

    def _init_portals(self, portals):
        for loc, portal in portals.items():
            pair = None
            entrance = None
            for neighbor in loc.neighbors():
                pair = portals.get(neighbor, pair)
                if neighbor in self.open:
                    entrance = neighbor

            name = "".join(sorted([portal, pair]))
            if name not in self.portals:
                self.portals[name] = []

            if entrance:
                self.portals[name].append(entrance)

        for portal, entrances in self.portals.items():
            assert len(entrances) <= 2

            for entrance in entrances:
                self.warp_portal[entrance] = portal

            if len(entrances) == 1:
                continue

            self.warps[entrances[0]] = entrances[1]
            self.warps[entrances[1]] = entrances[0]

            if self._is_outer(entrances[0]):
                self.outer_warps.add(entrances[0])
                assert not self._is_outer(entrances[1])
                self.inner_warps.add(entrances[1])
            else:
                self.inner_warps.add(entrances[0])
                assert self._is_outer(entrances[1])
                self.outer_warps.add(entrances[1])

    def _is_outer(self, warp):
        return warp.x in (2, self.cols-3) or warp.y in (2, self.rows-3)

    def min_steps(self):
        """ Return the minimum number of steps from 'AA' to 'ZZ' """
        start = self.portals['AA'][0]
        goal = self.portals['ZZ'][0]

        def _neighbors(vec):
            neighbors = list(vec.neighbors() & self.open)
            if vec in self.warps:
                neighbors.append(self.warps[vec])

            return neighbors

        def _heuristic(*_):
            return 0

        path = a_star(start, goal, neighbors=_neighbors, heuristic=_heuristic)
        return len(path) - 1

    def min_steps_recursive(self):
        """ Compute the minimum steps from 'AA' to 'ZZ' taking into
            account the recursive nature of the maze.
        """
        start = (self.portals['AA'][0], 0)
        goal = (self.portals['ZZ'][0], 0)

        def _neighbors(loc):
            vec, level = loc
            neighbors = [(neighbor, level)
                         for neighbor in vec.neighbors() & self.open]
            if vec in self.warps:
                if vec in self.outer_warps and level > 0:
                    neighbors.append((self.warps[vec], level - 1))
                elif vec in self.inner_warps:
                    neighbors.append((self.warps[vec], level + 1))

            return neighbors

        def _heuristic(*_):
            return 0

        path = a_star(start, goal, neighbors=_neighbors, heuristic=_heuristic)
        return len(path) - 1


@pytest.fixture(scope="module")
def tests():
    """ Fixture """
    return read_tests("day20_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, 23),
    (1, 58)
])
def test_min_steps(tests, index, expected):
    """ Test """
    maze = DonutMaze(tests[index])
    assert maze.min_steps() == expected


@pytest.mark.parametrize("index, expected", [
    (0, 26),
    (2, 396)
])
def test_min_steps_recursive(tests, index, expected):
    """ Test """
    maze = DonutMaze(tests[index])
    assert maze.min_steps_recursive() == expected


def _main():
    with open(asset("day20.txt")) as file:
        maze = DonutMaze(list(file))

    print("Part 1:", maze.min_steps())
    print("Part 2:", maze.min_steps_recursive())


if __name__ == "__main__":
    _main()
