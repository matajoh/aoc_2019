""" Solution for Day 18 """

from functools import lru_cache
from collections import deque

import pytest

from common import asset, read_tests, Vector


class Cave:
    """ Represents a cave containing keys and doors """

    def __init__(self, lines):
        self.entrances = set()
        self.keys = set()
        self.doors = set()
        self.door_keys = {}
        self.grid = {}
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                loc = Vector(x, y)
                if char == '#':
                    self.grid[loc] = '#'
                elif char == '.':
                    self.grid[loc] = '.'
                elif char == '@':
                    self.entrances.add(loc)
                    self.grid[loc] = '.'
                elif char.isalpha():
                    self.grid[loc] = char
                    if char.islower():
                        self.keys.add(loc)
                    else:
                        self.doors.add(loc)
                        self.door_keys[loc] = char.lower()
                else:
                    raise ValueError("Unexpected character: " + char)

    def _find_reachable(self, start, key_set):
        """ Returns all reachable states """
        keys = {}
        locs = deque([start])
        distances = {start: 0}
        while locs:
            loc = locs.popleft()
            if loc in self.keys:
                key = self.grid[loc]
                if key not in key_set:
                    keys[key] = distances[loc], loc
                    continue
            elif loc in self.doors:
                if self.door_keys[loc] not in key_set:
                    continue

            for neighbor in loc.neighbors():
                if self.grid[neighbor] == '#':
                    continue

                if neighbor in distances:
                    continue

                distances[neighbor] = distances[loc] + 1
                locs.append(neighbor)

        return [(loc, key, steps) for key, (steps, loc) in keys.items()]

    @staticmethod
    def _update_goal(goals, index, goal):
        return goals[:index] + (goal,) + goals[index+1:]

    def reachable(self, starts, key_set):
        """ Returns all reachable states """
        results = []
        for i, start in enumerate(starts):
            states = self._find_reachable(start, key_set)
            results.extend([(self._update_goal(starts, i, goal), key, steps)
                            for goal, key, steps in states])

        return results

    @lru_cache(maxsize=None)
    def score(self, starts, keys):
        """ Returns the minimum score at a step """
        if len(keys) == len(self.keys):
            return 0

        reachable = self.reachable(starts, keys)
        scores = [self.score(goals, "".join(sorted(keys + new_key))) + steps
                  for goals, new_key, steps in reachable]
        return min(scores)

    def min_steps(self):
        """ Computes the minimum number of steps to collect all keys """
        return self.score(tuple(self.entrances), "")


@pytest.fixture(scope="module")
def tests():
    """ Test fixture """
    return read_tests("day18_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, 8),
    (1, 86),
    (2, 132),
    (3, 136),
    (4, 81),
    (5, 8),
    (6, 24),
    (7, 32),
    (8, 72)
])
def test_find_key(tests, index, expected):  # pylint: disable=redefined-outer-name
    """ Test """
    cave = Cave(tests[index])
    assert cave.min_steps() == expected


def _main():
    with open(asset("day18.txt")) as file:
        cave = Cave(file)

    print("Part 1:", cave.min_steps())

    with open(asset("day18_part2.txt")) as file:
        cave = Cave(file)

    print("Part 2:", cave.min_steps())


if __name__ == "__main__":
    _main()
