""" Solution to Day 3 """

import os
from collections import namedtuple

import numpy as np
import pytest


EMPTY = ord('.')
ORIGIN = ord('o')
HORIZONTAL = ord('-')
VERTICAL = ord('|')
INTERSECTION = ord('X')
TURN = ord('+')
VERBOSE = False


class Point(namedtuple("Point", ["x", "y"])):
    """ A cartesian point """

    def left(self, distance):
        """ Move this point to the left """
        return Point(self.x - distance, self.y)

    def right(self, distance):
        """ Move this point to the right """
        return Point(self.x + distance, self.y)

    def up(self, distance):
        """ Move this point up """
        return Point(self.x, self.y - distance)

    def down(self, distance):
        """ Move this point down """
        return Point(self.x, self.y + distance)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def distance(self):
        """ Manhattan distance from this point to the origin """
        return abs(self.x) + abs(self.y)


class Segment(namedtuple("Segment", ["start", "end"])):
    """ A line segment """

    @property
    def is_horizontal(self):
        """ Whether this is a horizontal segment """
        return self.start.y == self.end.y

    def __len__(self):
        return (self.end - self.start).distance()

    def points(self):
        """ Return all the points in this segment """
        if self.is_horizontal:
            y = self.start.y
            start, end = reorder(self.start.x, self.end.x)
            for x in range(start, end+1):
                yield Point(x, y)
        else:
            x = self.start.x
            start, end = reorder(self.start.y, self.end.y)
            for y in range(start, end+1):
                yield Point(x, y)

    def contains(self, point):
        """ Whether a point falls on the segment """
        if self.is_horizontal:
            if point.y != self.start.y:
                return False

            start, end = reorder(self.start.x, self.end.x)
            return start <= point.x <= end
        else:
            if point.x != self.start.x:
                return False

            start, end = reorder(self.start.y, self.end.y)
            return start <= point.y <= end


class Rect(namedtuple("Rect", ["left", "top", "width", "height"])):
    """ A rectangle """

    @staticmethod
    def union(lhs, rhs):
        """ Returns the union of the two rectangles """
        left = min(lhs.left, rhs.left)
        top = min(lhs.top, rhs.top)
        right = max(lhs.right, rhs.right)
        bottom = max(lhs.bottom, rhs.bottom)
        return Rect(left, top, right-left, bottom-top)

    def expand(self):
        """ Expands the rectangle by one value in all directions """
        return Rect(self.left - 1, self.top - 1, self.width + 2, self.height + 2)

    @property
    def right(self):
        """ The right-most column """
        return self.left + self.width

    @property
    def bottom(self):
        """ The bottom-most row """
        return self.top + self.height


def reorder(a, b):
    """ Reorder the arguments so they are ascending """
    if b < a:
        return b, a

    return a, b


class Wire:
    """ A wire made up of segments """
    def __init__(self, directions):
        directions = directions.split(",")
        self.segments = []
        start = Point(0, 0)
        left = 0
        right = 0
        top = 0
        bottom = 0
        points = []
        for direction in directions:
            distance = int(direction[1:])
            if direction[0] == 'L':
                end = start.left(distance)
            elif direction[0] == 'R':
                end = start.right(distance)
            elif direction[0] == 'U':
                end = start.up(distance)
            elif direction[0] == 'D':
                end = start.down(distance)
            else:
                raise NotImplementedError(
                    "Unsupported direction: " + direction[0])

            left = min(left, end.x)
            right = max(right, end.x)
            top = min(top, end.y)
            bottom = max(bottom, end.y)
            segment = Segment(start, end)
            points.extend(segment.points())
            self.segments.append(Segment(start, end))
            start = end

        self.bounds = Rect(left, top, right-left+1, bottom-top+1)
        self.points = set(points)

    def steps_to(self, point):
        """ Determine the number of steps to the given point """
        steps = 0
        for segment in self.segments:
            if segment.contains(point):
                steps += (point - segment.start).distance()
                break
            else:
                steps += len(segment)

        return steps

    def draw(self):
        """ Draw the wire onto a 2D grid """
        print("Drawing wire...")
        grid = np.zeros((self.bounds.height, self.bounds.width), np.uint8)
        grid[:] = EMPTY
        offset = Point(self.bounds.left, self.bounds.top)
        for segment in self.segments:
            start = segment.start - offset
            end = segment.end - offset
            if segment.is_horizontal:
                row = start.y
                start, end = reorder(start.x, end.x)
                end += 1

                for col in range(start, end):
                    if grid[row, col] != EMPTY:
                        grid[row, col] = TURN
                    else:
                        grid[row, col] = HORIZONTAL
            else:
                col = start.x
                start, end = reorder(start.y, end.y)
                end += 1

                for row in range(start, end):
                    if grid[row, col] != EMPTY:
                        grid[row, col] = TURN
                    else:
                        grid[row, col] = VERTICAL

        origin = Point(0, 0) - offset
        grid[origin.y, origin.x] = ORIGIN
        return grid


def to_string(grid):
    """ Convert a grid to a string """
    return "\n".join(["".join([chr(val) for val in row]) for row in grid])


def parse_wires(dir0, dir1):
    """ Parse the wire from the text """
    print("Parsing...")
    wire0 = Wire(dir0)
    wire1 = Wire(dir1)
    bounds = Rect.union(wire0.bounds, wire1.bounds).expand()
    wire0.bounds = wire1.bounds = bounds
    return wire0, wire1


def combine(grid0: np.ndarray, grid1: np.ndarray, offset: Point):
    """ Create a combination of the two grids """
    print("Combining...")
    combo = np.zeros(grid0.shape, np.uint8)
    combo[:] = EMPTY
    mask0 = grid0 != EMPTY
    mask1 = grid1 != EMPTY
    combo[mask0] = grid0[mask0]
    combo[mask1] = grid1[mask1]
    combo[mask0 * mask1] = INTERSECTION
    origin = Point(0, 0) - offset
    combo[origin.y, origin.x] = ORIGIN

    return combo


def find_intersections(wire0: Wire, wire1: Wire):
    """ Finds intersections between the two wires """
    print("Finding the intersections...")
    points = wire0.points & wire1.points
    points.remove(Point(0, 0))
    return points

def find_min_dist(points):
    """ Finds the minimum distance """
    print("Finding minimum distance...")
    return min(map(lambda point: point.distance(), points))


def find_min_steps(wire0, wire1, points):
    """ Finds the minimum combined number of steps """
    print("Finding minimum steps...")
    return min(map(lambda point: wire0.steps_to(point) + wire1.steps_to(point), points))


@pytest.mark.parametrize("dir0, dir1, expected", [
    ("R8,U5,L5,D3", "U7,R6,D4,L4", 6),
    ("R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", 159),
    ("R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
     "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", 135)
])
def test_min_dist(dir0, dir1, expected):
    """ Test the minimum distance function """
    wire0, wire1 = parse_wires(dir0, dir1)
    points = find_intersections(wire0, wire1)
    actual = find_min_dist(points)
    assert actual == expected


@pytest.mark.parametrize("dir0, dir1, expected", [
    ("R8,U5,L5,D3", "U7,R6,D4,L4", 30),
    ("R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", 610),
    ("R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
     "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", 410)
])
def test_min_steps(dir0, dir1, expected):
    """ Test the minimum steps function """
    wire0, wire1 = parse_wires(dir0, dir1)
    points = find_intersections(wire0, wire1)
    actual = find_min_steps(wire0, wire1, points)
    assert actual == expected


def _main():
    with open(os.path.join("..", "inputs", "day3.txt")) as file:
        dir0, dir1 = file

    wire0, wire1 = parse_wires(dir0, dir1)
    points = find_intersections(wire0, wire1)
    min_dist = find_min_dist(points)
    print("Part 1:", min_dist)

    min_steps = find_min_steps(wire0, wire1, points)
    print("Part 2:", min_steps)


if __name__ == "__main__":
    _main()
