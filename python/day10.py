""" Solution for day 10 """

import os
import math
from collections import namedtuple, OrderedDict

from sortedcontainers import SortedList
import pytest

class Point(namedtuple("Point", ["x", "y"])):
    """ Point class """

class Ray(namedtuple("Ray", ["angle", "length", "start", "end"])):
    """ A ray from one point to another """

    @staticmethod
    def create(start: Point, end: Point) -> "Ray":
        """ Create a ray from one point to another """
        dx = end.x - start.x
        dy = end.y - start.y
        angle = math.atan2(dy, dx) + (math.pi / 2)

        if angle < 0:
            angle += math.tau

        length = dx*dx + dy*dy
        return Ray(angle, length, start, end)


def parse_points(path):
    """ Parse the points into a list """
    points = []
    with open(path) as file:
        for y, line in enumerate(file):
            points.extend([Point(x, y) for x, char in enumerate(line) if char == '#'])

    return points


def compute_rays(points):
    """ Compute all the rays from each point to every other point """
    rays = {}
    for start in points:
        rays[start] = SortedList([Ray.create(start, end) for end in points if start != end])

    return rays


def compute_seen(rays):
    """ Compute which points are unobstructed """
    seen = OrderedDict()
    for ray in rays:
        if ray.angle not in seen:
            seen[ray.angle] = ray

    return list(seen.values())


def find_best_position(path):
    """ Find the position which can see the most points """
    points = parse_points(path)
    rays = compute_rays(points)
    num_seen = {point: len(compute_seen(ray)) for point, ray in rays.items()}
    best = max(num_seen, key=num_seen.get)
    return best, rays[best], num_seen[best]


def fire_laser(rays):
    """ Fire the laser.

        Obliterate all asteroids, and record the order in which they
        are destroyed
    """
    fire_order = []
    while rays:
        seen = compute_seen(rays)
        fire_order.extend([ray.end for ray in seen])
        for ray in seen:
            rays.remove(ray)

    return fire_order

@pytest.mark.parametrize("path, expected", [
    ("test0", ((3, 4), 8)),
    ("test1", ((5, 8), 33)),
    ("test2", ((1, 2), 35)),
    ("test3", ((6, 3), 41)),
    ("test4", ((11, 13), 210))
])
def test_find_best_position(path, expected):
    """ Test """
    path = os.path.join(os.path.dirname(__file__), "..", "inputs", "day10_" + path + ".txt")
    best, _, num_seen = find_best_position(path)
    assert (best, num_seen) == expected


def test_fire_layer():
    """ Test """
    path = os.path.join(os.path.dirname(__file__), "..", "inputs", "day10_test4.txt")
    _, rays, _ = find_best_position(path)
    fire_order = fire_laser(rays)
    assert fire_order[0] == (11, 12)
    assert fire_order[1] == (12, 1)
    assert fire_order[2] == (12, 2)
    assert fire_order[9] == (12, 8)
    assert fire_order[19] == (16, 0)
    assert fire_order[49] == (16, 9)
    assert fire_order[99] == (10, 16)
    assert fire_order[198] == (9, 6)
    assert fire_order[199] == (8, 2)
    assert fire_order[200] == (10, 9)
    assert fire_order[-1] == (11, 1)


def _main():
    path = os.path.join("..", "inputs", "day10.txt")
    _, rays, num_seen = find_best_position(path)
    print("Part 1:", num_seen)

    fire_order = fire_laser(rays)
    point200 = fire_order[199]
    print("Part 2:", point200.x*100 + point200.y)


if __name__ == "__main__":
    _main()
