import csv
import math
import os

import pytest


def fuelFor(mass: int) -> int:
    return int(math.floor(mass/3) - 2)


def totalFuelFor(mass: int) -> int:
    fuel = fuelFor(mass)
    if fuel <= 0:
        return 0
    
    return fuel + totalFuelFor(fuel)

@pytest.mark.parametrize("input, output", [
    (12, 2),
    (14, 2),
    (1969, 654),
    (100756, 33583)
])
def test_fuelFor(input, output):
    assert fuelFor(input) == output


@pytest.mark.parametrize("input, output", [
    (14, 2),
    (1969, 966),
    (100756, 50346)
])
def test_totalFuelFor(input, output):
    assert totalFuelFor(input) == output


def part1(mass):
    fuel = sum([fuelFor(m) for m in mass])
    print("part1:", fuel)


def part2(mass):
    fuel = sum([totalFuelFor(m) for m in mass])
    print("part2:", fuel)


def _main():
    with open(os.path.join("inputs", "day1.txt")) as file:
        mass = [int(line) for line in file]

    part1(mass)
    part2(mass)


if __name__ == "__main__":
    _main()
