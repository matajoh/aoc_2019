""" Solution for Day 7 """

import os

class Body:
    """ Represents an orbiting body.

    Args:
        name: the name of the body
    """

    def __init__(self, name: str):
        self.satellites = []
        self.name = name

    def add_satellite(self, body: "Body"):
        """ Add a satellite to this body """
        self.satellites.append(body)

    def count_orbits(self, depth: int) -> int:
        """ Count the number of direct and indirect orbits """
        if not self.satellites:
            return depth

        orbits = depth + sum([satellite.count_orbits(depth + 1)
                              for satellite in self.satellites])
        return orbits

    def find(self, name: str) -> int:
        """ Find a named body in this body's orbit list """
        if self.name == name:
            return 1

        distances = list(filter(None, [body.find(name) for body in self.satellites]))
        if distances:
            return min(distances) + 1

        return None

    def find_shortest_transfer(self, name0: str, name1: str) -> int:
        """ Find the shortest orbital transfer between two bodies """
        if not self.satellites:
            return None

        distances0 = list(filter(None, [body.find(name0)
                                        for body in self.satellites]))
        distances1 = list(filter(None, [body.find(name1)
                                        for body in self.satellites]))

        if not(distances0 and distances1):
            return None

        path_distance = list(filter(None, [body.find_shortest_transfer(name0, name1)
                                           for body in self.satellites]))
        if path_distance:
            return min(path_distance)

        return min(distances0) + min(distances1) - 2

    @staticmethod
    def parse(orbits: str) -> "Body":
        """ Parse a body and its orbits from a string """
        com = Body("COM")
        lookup = {com.name: com}

        for orbit in orbits.split("\n"):
            body0, body1 = orbit.split(')')
            if body0 not in lookup:
                lookup[body0] = Body(body0)

            if body1 not in lookup:
                lookup[body1] = Body(body1)

            lookup[body0].add_satellite(lookup[body1])

        return com


TEST0 = """COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L"""

TEST1 = """COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN"""


def test_count_orbits():
    """ Test the count orbits method """
    com = Body.parse(TEST0)
    assert com.count_orbits(0) == 42


def test_shortest_transfer():
    """ Test the shortest transfer method """
    com = Body.parse(TEST1)
    assert com.find_shortest_transfer("YOU", "SAN") == 4


def _main():
    with open(os.path.join("inputs", "day6.txt")) as file:
        com = Body.parse(file.read())

    print("part1:", com.count_orbits(0))
    print("part2:", com.find_shortest_transfer("YOU", "SAN"))


if __name__ == "__main__":
    _main()
