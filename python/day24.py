""" Solution to day 24 """

import itertools
from collections import namedtuple
from functools import lru_cache

from common import asset, read_tests, Vector


def _parse_bugs(lines):
    bugs = set()
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                bugs.add(Vector(x, y))

    return bugs


POS = [Vector(x, y) for x, y in itertools.product(range(5), range(5))]


def _step(current_bugs):
    next_bugs = set()

    for pos in POS:
        num_bugs = sum(
            [neighbor in current_bugs for neighbor in pos.neighbors()])
        if pos in current_bugs:
            if num_bugs == 1:
                next_bugs.add(pos)
        elif num_bugs in (1, 2):
            next_bugs.add(pos)

    return next_bugs


POWERS = [2 ** power for power in range(25)]


def _biodiversity_rating(bugs):
    return sum(POWERS[bug.y*5 + bug.x] for bug in bugs)


def find_first_repeat(lines):
    """ Find the first repeating pattern's biodiversity rating """
    bugs = _parse_bugs(lines)

    biodiversities = set([_biodiversity_rating(bugs)])
    while True:
        bugs = _step(bugs)
        biodiversity = _biodiversity_rating(bugs)
        if biodiversity in biodiversities:
            return biodiversity

        biodiversities.add(biodiversity)


def test_step():
    """ Test """
    states = read_tests("day24_tests.txt")
    bugs = _parse_bugs(states[0])
    for lines in states[1:]:
        expected_bugs = _parse_bugs(lines)
        bugs = _step(bugs)
        assert bugs == expected_bugs


def test_first_repeat():
    """ Test """
    lines = read_tests("day24_tests.txt")[0]
    assert find_first_repeat(lines) == 2129920


class Plutonian(namedtuple("Plutonian", ["level", "x", "y"])):
    """ A plutonian recursive location """

    def __add__(self, other):
        return Plutonian(self.level + other.level, self.x + other.x, self.y + other.y)

    @lru_cache(maxsize=None)
    def neighbors(self):
        """ Plutonian neighbors """
        result = []
        for dx, dy in zip([0, 0, -1, 1], [-1, 1, 0, 0]):
            new_x = self.x + dx
            new_y = self.y + dy
            if new_x == 0 and new_y == 0:
                level = self.level + 1
                if self.x < 0:
                    result.extend([Plutonian(level, -2, y)
                                   for y in range(-2, 3)])
                elif self.x > 0:
                    result.extend([Plutonian(level, 2, y)
                                   for y in range(-2, 3)])
                elif self.y < 0:
                    result.extend([Plutonian(level, x, -2)
                                   for x in range(-2, 3)])
                else:
                    result.extend([Plutonian(level, x, 2)
                                   for x in range(-2, 3)])
            elif new_x == -3:
                result.append(Plutonian(self.level - 1, -1, 0))
            elif new_x == 3:
                result.append(Plutonian(self.level - 1, 1, 0))
            elif new_y == -3:
                result.append(Plutonian(self.level - 1, 0, -1))
            elif new_y == 3:
                result.append(Plutonian(self.level - 1, 0, 1))
            else:
                result.append(Plutonian(self.level, new_x, new_y))

        return result


def _parse_bugs_recursive(lines):
    bugs = set()
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                bugs.add(Plutonian(0, x-2, y-2))

    return bugs


def _step_recursive(current_bugs):
    potential_bugs = current_bugs.copy()
    for bug in current_bugs:
        potential_bugs |= set(bug.neighbors())

    next_bugs = set()

    for pos in potential_bugs:
        num_bugs = sum(
            [neighbor in current_bugs for neighbor in pos.neighbors()])
        if pos in current_bugs:
            if num_bugs == 1:
                next_bugs.add(pos)
        elif num_bugs in (1, 2):
            next_bugs.add(pos)

    return next_bugs


def _print_recursive(bugs):
    min_level = min(bug.level for bug in bugs)
    max_level = max(bug.level for bug in bugs)

    for level in range(min_level, max_level + 1):
        print("Depth {}:".format(level))
        lines = []
        for y in range(-2, 3):
            chars = []
            for x in range(-2, 3):
                if Plutonian(level, x, y) in bugs:
                    chars.append('#')
                else:
                    chars.append('.')

            if y == 0:
                chars[2] = '?'

            lines.append("".join(chars))

        print("\n".join(lines))
        print()


def test_step_recursive():
    """ Test """
    lines = read_tests("day24_tests.txt")[0]
    bugs = _parse_bugs_recursive(lines)
    for _ in range(10):
        bugs = _step_recursive(bugs)
        print(len(bugs))

    _print_recursive(bugs)

    assert len(bugs) == 99


def simulate_recursive(lines, minutes):
    """ Run a recursive simulation """
    bugs = _parse_bugs_recursive(lines)
    for _ in range(minutes):
        bugs = _step_recursive(bugs)

    return len(bugs)


def _main():
    with open(asset("day24.txt")) as file:
        lines = list(file)

    print("Part 1:", find_first_repeat(lines))
    print("Part 2:", simulate_recursive(lines, 200))


if __name__ == "__main__":
    _main()
