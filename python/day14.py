""" Solution to day 14 """

#pylint: disable=redefined-outer-name

from collections import namedtuple
from typing import List
import heapq

import pytest

from common import asset, read_tests


class Reagent(namedtuple("Chemical", ["name", "count"])):
    """ Class representing a reagent in a reaction """

    @staticmethod
    def parse(line: str) -> "Reagent":
        """ Parse the reagent from a string """
        count, name = line.split()
        return Reagent(name.strip(), int(count))

    def __repr__(self):
        return "{} {}".format(self.count, self.name)


class Reaction(namedtuple("Reaction", ["inputs", "output"])):
    """ Represents a chemical reaction.

    Args:
        inputs: a list of Reagents
        output: the output reagent
    """

    @staticmethod
    def parse(line: str) -> "Reaction":
        """ Parse a reaction from a string """
        inputs, output = line.split('=>')
        inputs = [Reagent.parse(part) for part in inputs.split(',')]
        output = Reagent.parse(output)
        return Reaction(inputs, output)

    def num_to_produce(self, count):
        """ Computer the number of reactions needed to product
            a target quantity of output.

        Args:
            count: the number of outputs needed

        Returns:
            the number of reactions to achieve the target output
        """
        if count % self.output.count == 0:
            return count // self.output.count

        return (count // self.output.count) + 1

    def __repr__(self):
        return "{} => {}".format(" ".join([str(i) for i in self.inputs]), self.output)


class Nanofactory:
    """ Represents a nanofactory that produces fuel from ore.

    Args:
        reactions: the reactions used by this factory
    """
    def __init__(self, reactions: List[Reaction]):
        self._reactions = {}
        for reaction in reactions:
            self._reactions[reaction.output.name] = reaction

        self._reactions["ORE"] = None

        distances = {name: self._ore_distance(name, 0)
                     for name in self._reactions}
        max_dist = max(distances.values())
        self._priority = {name: max_dist - dist
                          for name, dist in distances.items()}

    def _ore_distance(self, name: str, depth: int) -> int:
        if name == "ORE":
            return depth

        return max([self._ore_distance(ing.name, depth+1)
                    for ing in self._reactions[name].inputs])

    def compute_ore_for_fuel(self, count=1) -> int:
        """ Compute the amount of ore needed to produce fuel.

        Keyword Args:
            count: the target quantity of fuel [1]

        Returns:
            the quantity of ore required
        """
        counts = {"FUEL": count}
        ingredients = [(0, "FUEL")]

        while ingredients:
            _, name = heapq.heappop(ingredients)
            if name == "ORE":
                continue

            num_needed = counts[name]
            reaction = self._reactions[name]
            num_reactions = reaction.num_to_produce(num_needed)
            for ing in reaction.inputs:
                if ing.name not in counts:
                    heapq.heappush(
                        ingredients, (self._priority[ing.name], ing.name))
                    counts[ing.name] = 0

                counts[ing.name] += ing.count * num_reactions

        return counts["ORE"]

    def compute_fuel_for_ore(self, ore: int) -> int:
        """ Compute the maximum quantity of fuel that can be produced.

        Args:
            ore: the quantity of ore available

        Returns:
            the maximum quantity of fuel
        """
        start = int(ore / self.compute_ore_for_fuel())
        end = start*3//2
        while start != end - 1:
            mid = (start + end) // 2
            ore_needed = self.compute_ore_for_fuel(mid)
            if ore_needed < ore:
                start = mid
            else:
                end = mid

        return start

    @staticmethod
    def parse(lines: List[str]) -> "Nanofactory":
        """ Parse a nanofactory from a string """
        reactions = [Reaction.parse(line) for line in lines]
        return Nanofactory(reactions)


@pytest.fixture(scope="module")
def tests():
    """ Test fixture """
    return read_tests("day14_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, 31),
    (1, 165),
    (2, 13312),
    (3, 180697),
    (4, 2210736)
])
def test_compute_ore(tests, index, expected):
    """ Test """
    factory = Nanofactory.parse(tests[index])
    assert factory.compute_ore_for_fuel() == expected


@pytest.mark.parametrize("index, expected", [
    (2, 82892753),
    (3, 5586022),
    (4, 460664)
])
def test_total_fuel(tests, index, expected):
    """ Test """
    factory = Nanofactory.parse(tests[index])
    assert factory.compute_fuel_for_ore(1000000000000) == expected


def _main():
    with open(asset("day14.txt")) as file:
        factory = Nanofactory.parse(file.readlines())

    ore_needed = factory.compute_ore_for_fuel()
    print("Part 1:", ore_needed)

    total_fuel = factory.compute_fuel_for_ore(1000000000000)
    print("Part 2:", total_fuel)


if __name__ == "__main__":
    _main()
