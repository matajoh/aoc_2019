""" Solution for Day 18 """

import pytest

from common import a_star, asset, read_tests, Vector, Neighbors

# TODO get record of keys grabbed for minimum steps
# TODO create animations!!!




class Cave:
    """ Represents a cave containing keys and doors """

    def __init__(self, lines):
        self.open = set()
        self.entrances = set()
        self.walls = set()
        self.keys = set()
        self.doors = set()
        self.item_loc = {}
        self.loc_item = {}
        self.scores = {}
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                loc = Vector(x, y)
                if char == '#':
                    self.walls.add(loc)
                elif char == '.':
                    self.open.add(loc)
                elif char == '@':
                    self.entrances.add(loc)
                    self.open.add(loc)
                elif char.isalpha():
                    if char.islower():
                        self.keys.add(loc)
                    else:
                        self.doors.add(loc)

                    self.item_loc[char] = loc
                    self.loc_item[loc] = char
                else:
                    raise ValueError("Unexpected character: " + char)

        self.not_reachable = set()
        reachable = []
        nodes = self.open | self.keys | self.doors | self.entrances
        neighbors = Neighbors(nodes)
        for start in self.entrances:
            goals = set()
            for goal in self.keys:
                if (start, goal) in self.not_reachable:
                    continue

                path = a_star(start, goal, neighbors)
                if path:
                    goals.add(goal)
            
            reachable.append(goals)
        
        for i, entrance in enumerate(self.entrances):
            reachable_goals = set()
            unreachable_goals = set()
            for j, goals in enumerate(reachable):
                if i == j:
                    reachable_goals |= goals
                else:
                    unreachable_goals |= goals
            
            for goal in unreachable_goals:
                self.not_reachable.add((entrance, goal))
                for start in reachable_goals:
                    self.not_reachable.add((start, goal))


    def reachable(self, starts, keys):
        """ Returns all reachable states """
        nodes = {self.item_loc[key] for key in keys}
        nodes |= {self.item_loc[key.upper()]
                  for key in keys if key.upper() in self.item_loc}
        nodes |= self.open
        for goal in self.keys:
            key = self.loc_item[goal]
            if key in keys:
                continue

            for i, start in enumerate(starts):
                if (start, goal) in self.not_reachable:
                    continue

                path = a_star(start, goal, Neighbors(nodes | {goal}))
                if path:
                    goals = starts[:i] + (goal,) + starts[i+1:]
                    yield goals, key, len(path) - 1

    def score(self, starts, keys):
        """ Returns the minimum score at a step """
        obtained = "".join(keys)
        lookup = starts + (obtained,)
        if lookup not in self.scores:
            if len(keys) == len(self.keys):
                return 0

            self.scores[lookup] = min([self.score(goals, {new_key} | keys) + steps
                                       for goals, new_key, steps
                                       in self.reachable(starts, keys)])

        return self.scores[lookup]

    def min_steps(self):
        """ Computes the minimum number of steps to collect all keys """
        return self.score(tuple(self.entrances), set())


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
def test_find_key(tests, index, expected): #pylint: disable=redefined-outer-name
    """ Test """
    cave = Cave(tests[index])
    assert cave.min_steps() == expected


def _main():
    #with open(asset("day18.txt")) as file:
    #    cave = Cave(file)

    #print("Part 1:", cave.min_steps())

    with open(asset("day18_part2.txt")) as file:
        cave = Cave(file)

    print("Part 2:", cave.min_steps())


if __name__ == "__main__":
    _main()
