""" Solution for Day 19 """

from collections import namedtuple

import numpy as np

from common import asset
from intcode import Computer


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

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

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

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


def _move_test(computer, x, y):
    computer.reset()
    computer.run_to_input()
    computer.write(x)
    computer.write(y)
    computer.run_to_output()
    return computer.read()


def _scan_emitter(computer, left, top, width, height):
    scan = np.zeros((width, height), np.uint8)

    for x in range(0, width):
        for y in range(0, height):
            scan[y, x] = _move_test(computer, left + x, top + y)

    return scan


def _walk_top(computer, start, end):
    current = start
    sequence = []
    while current.x < end and current.y < end:
        sequence.append(current)
        right = current + Directions[RIGHT]
        if _move_test(computer, right.x, right.y):
            current = right
        else:
            current = current + Directions[DOWN]

    return sequence


def _walk_bottom(computer, start, end):
    current = start
    sequence = []
    while current.x < end and current.y < end:
        sequence.append(current)
        down = current + Directions[DOWN]
        if _move_test(computer, down.x, down.y):
            current = down
        else:
            current = current + Directions[RIGHT]

    return sequence


def _principal_period(s):
    i = (s+s).find(s, 1, -1)
    return None if i == -1 else s[:i]


def _line(points):
    mean = sum(points, Vector(0, 0)) / len(points)
    norm_points = [point - mean for point in points]
    sum_xy = sum(point.x*point.y for point in norm_points)
    sum_xx = sum(point.x*point.x for point in norm_points)
    slope = sum_xy / sum_xx
    intercept = mean.y - slope*mean.x
    return slope, intercept


def _estimate_box_from_lines(computer, size):
    top = _walk_top(computer, Vector(13, 16), 50)
    bottom = _walk_bottom(computer, Vector(13, 16), 50)

    m0, b0 = _line(top)
    m1, b1 = _line(bottom)

    y0 = b1 - (m1/m0)*b0 - size*m1 - size
    y0 /= 1 - (m1/m0)
    x0 = (y0 - b0)/m0
    y1 = y0 + size
    x1 = x0 - size

    top_right = Vector(int(x0), int(y0))
    bottom_left = Vector(int(x1), int(y1))
    return top_right, bottom_left


def _get_samples_around_estimate(computer, estimate, search, is_top):
    estimate -= Vector(search//2, search//2)
    scan = _scan_emitter(computer, estimate.x, estimate.y, search, search)

    samples = []
    for y, x in np.transpose(np.nonzero(scan)):
        if x == search-1 or y == search-1:
            continue

        loc = Vector(x, y)
        if is_top:
            up = loc + Directions[UP]
            right = loc + Directions[RIGHT]
            if scan[up.y, up.x] and scan[right.y, right.x]:
                continue
        else:
            down = loc + Directions[DOWN]
            left = loc + Directions[LEFT]
            if not(scan[left.y, left.x] == 0 or scan[down.y, down.x] == 0):
                continue

        samples.append(loc + estimate)

    return samples


def _find_location(computer, size=100, search=30):
    top_right, bottom_left = _estimate_box_from_lines(computer, size)
    top = _get_samples_around_estimate(computer, top_right, search, True)
    bottom = _get_samples_around_estimate(computer, bottom_left, search, True)
    candidates = []
    for top_right in top:
        for bottom_left in bottom:
            width = top_right.x - bottom_left.x + 1
            height = bottom_left.y - top_right.y + 1
            if width == size and height == size:
                candidates.append(Vector(bottom_left.x, top_right.y))

    return min(candidates, key=lambda vec: vec.length)


def _main():
    with open(asset("day19.txt")) as file:
        program = [int(code) for code in file.read().split(',')]

    computer = Computer(program)

    scan = _scan_emitter(computer, 0, 0, 50, 50)
    print("Part 1:", scan.sum())

    loc = _find_location(computer)
    print("Part 2:", loc.x*10000 + loc.y)


if __name__ == "__main__":
    _main()
