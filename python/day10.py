import os
from decimal import Decimal
from collections import namedtuple

import pytest

class Point(namedtuple("Point", ["x", "y"])):
    """ Point class """

class Line(namedtuple("Line", ["m", "b"])):
    @staticmethod
    def create(lhs: Point, rhs: Point) -> "Line":
        if lhs.x == rhs.x:
            return Line(Decimal(0), Decimal(-lhs.x))
        
        dy = rhs.y - lhs.y
        dx = rhs.x - lhs.x
        m = Decimal(dy) / Decimal(dx)
        b = lhs.y - m*lhs.x
        return Line(m, b)

def parse_points(path):
    points = []
    with open(path) as file:
        for y, line in enumerate(file):
            points.extend([Point(x, y) for x, char in enumerate(line) if char == '#'])

    return points


def count_detections(points):
    num_points = len(points)
    point_to_lines = {point: set() for point in points}
    line_to_points = {}
    for i in range(num_points):
        lhs = points[i]
        for j in range(i+1, num_points):
            rhs = points[j]
            line = Line.create(points[i], points[j])
            if line not in line_to_points:
                line_to_points[line] = set()
            
            line_to_points[line].add(lhs)
            line_to_points[line].add(rhs)
            point_to_lines[lhs].add(line)
            point_to_lines[rhs].add(line)

    result = {}
    for point, lines in point_to_lines.items():
        result[point] = len(lines)
       
    return result


def find_best_position(path):
    points = parse_points(path)
    detections = count_detections(points)
    point = max(detections, key=detections.get)
    return point, detections[point]

@pytest.mark.parametrize("path, expected", [
    ("test0", ((3, 4), 8)),
    ("test1", ((5, 8), 33)),
    ("test2", ((1, 2), 35)),
    ("test3", ((6, 3), 41)),
    ("test4", ((11, 13), 210))
])
def test_find_best_position(path, expected):
    path = os.path.join("..", "inputs", "day10_" + path + ".txt")
    actual = find_best_position(path)
    assert actual == expected


def _main():
    path = os.path.join("..", "inputs", "day10_test0.txt")
    print("Part 1:", find_best_position(path))


if __name__ == "__main__":
    _main()
