""" Solution to Day 1 """

import math

import pytest

from common import asset


def fuelFor(mass: int) -> int:
    """ Compute the fuel needed to lift the provided mass """
    return int(math.floor(mass/3) - 2)


def totalFuelFor(mass: int) -> int:
    """ Compute the fuel needed to lift the mass, and all the fuel """
    fuel = fuelFor(mass)
    if fuel <= 0:
        return 0

    return fuel + totalFuelFor(fuel)

@pytest.mark.parametrize("mass, fuel", [
    (12, 2),
    (14, 2),
    (1969, 654),
    (100756, 33583)
])
def test_fuelFor(mass, fuel):
    """ Test """
    assert fuelFor(mass) == fuel


@pytest.mark.parametrize("mass, fuel", [
    (14, 2),
    (1969, 966),
    (100756, 50346)
])
def test_totalFuelFor(mass, fuel):
    """ Test """
    assert totalFuelFor(mass) == fuel


def _main():
    with open(asset("day1.txt")) as file:
        mass = [int(line) for line in file]

    fuel = sum([fuelFor(m) for m in mass])
    print("part1:", fuel)

    fuel = sum([totalFuelFor(m) for m in mass])
    print("part2:", fuel)


if __name__ == "__main__":
    _main()
