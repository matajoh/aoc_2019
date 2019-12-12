import os
import sys
from collections import namedtuple
import math
import itertools

import pytest
import numpy as np
import matplotlib.pyplot as plt


class Vector(namedtuple("Vector", ["x", "y", "z"])):
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def velocity(self, other: "Vector"):
        return Vector(1 if self.x < other.x else (-1 if self.x > other.x else 0),
                      1 if self.y < other.y else (-1 if self.y >
                                                  other.y else 0),
                      1 if self.z < other.z else (-1 if self.z > other.z else 0))

    def __repr__(self) -> str:
        return "<x={}, y={}, z={}>".format(*self)

    def energy_repr(self) -> str:
        vals = [abs(val) for val in self] + [self.energy]
        return "{} + {} + {} = {}".format(*vals)

    @property
    def energy(self) -> int:
        return sum([abs(val) for val in self])

    @staticmethod
    def parse(line) -> "Vector":
        assert line[:3] == "<x="
        line = line[3:]
        end = line.find(',')
        x = int(line[:end])
        line = line[end:]
        assert line[:4] == ", y="
        line = line[4:]
        end = line.find(',')
        y = int(line[:end])
        line = line[end:]
        assert line[:4] == ', z='
        line = line[4:]
        end = line.find('>')
        z = int(line[:end])
        assert line[end] == '>'

        return Vector(x, y, z)


class Sequence:
    def __init__(self, values):
        self.values = values
    
    def add(self, value):
        self.values.pop(0)
        self.values.append(value)
    
    def __eq__(self, other):
        for lhs, rhs in zip(self.values, other.values):
            if lhs != rhs:
                return False
        
        return True
    
    def __hash__(self):
        return sum([value.__hash__() for value in self.values])


class Moon:
    def __init__(self, position: Vector):
        self.position = position
        self.velocity = Vector(0, 0, 0)

    def update_velocity(self, other: "Moon"):
        self.velocity += self.position.velocity(other.position)

    def update_position(self):
        self.position += self.velocity

    @property
    def energy(self) -> int:
        return self.position.energy * self.velocity.energy

    def __repr__(self) -> str:
        return "pos={}, vel={}".format(self.position, self.velocity)

    def energy_repr(self) -> str:
        pot = self.position.energy
        kin = self.position.energy
        total = pot + kin
        return "pot {};  kin: {};  total: {} * {} = {}".format(
            self.position.energy_repr(),
            self.velocity.energy_repr(),
            pot,
            kin,
            total
        )


def _print_state(step, moons):
    print("After {} steps:".format(step))
    for moon in moons:
        print(moon)

    print()


def _simulate_movement(moons, steps, record=None):
    _print_state(0, moons)
    interval = steps // 10
    for step in range(steps):
        if record is not None:
            record.append([moon.position for moon in moons])

        for moon0, moon1 in itertools.combinations(moons, 2):
            moon0.update_velocity(moon1)
            moon1.update_velocity(moon0)

        for moon in moons:
            moon.update_position()

        if (step+1) % interval == 0:
            _print_state(step + 1, moons)

    print("Energy after {} steps:".format(steps))
    for moon in moons:
        print(moon.energy_repr())

    energies = [moon.energy for moon in moons]
    total_energy = sum(energies)
    print("Sum of total energy: {} = {}".format(
        " + ".join([str(energy) for energy in energies]),
        total_energy
    ))

    return total_energy


def _find_periods(moons):
    record = []
    _simulate_movement(moons, 500000, record)

    periods = [0]*len(moons)

    sequences = [Sequence([state[i] for state in record[:1000]]) for i in range(4)]
    test_sequences = [Sequence([state[i] for state in record[:1000]]) for i in range(4)]
    for i, state in enumerate(record[1000:]):
        for j, expected in enumerate(sequences):
            if test_sequences[j] == expected:
                if periods[j] == 0:
                    periods[j] = i
        
        for j, sequence in enumerate(test_sequences):
            sequence.add(state[j])

    print(periods)
    return periods


@pytest.mark.parametrize("path, steps, energy", [
    ("day12_test0.txt", 10, 179),
    ("day12_test1.txt", 100, 1940)
])
def test_simulate_movement(path, steps, energy):
    with open(os.path.join("..", "inputs", path)) as file:
        moons = [Moon(Vector.parse(line)) for line in file]

    assert _simulate_movement(moons, steps, steps // 10) == energy


def compute_gcd(x, y):
   while(y):
       x, y = y, x % y
   return x

def compute_lcm(x, y):
   lcm = (x*y)//compute_gcd(x,y)
   return lcm

def _main():
    with open(os.path.join("..", "inputs", "day12.txt")) as file:
        initial_state = [Vector.parse(line) for line in file]
    
    moons = [Moon(pos) for pos in initial_state]

    record = []
    energy = _simulate_movement(moons, 1000, record)
    print("Part 1:", energy)

    periods = _find_periods(moons)
    lcm = compute_lcm(periods[0], periods[1])
    lcm = compute_lcm(lcm, periods[2])
    print("Part 2:", lcm)


if __name__ == "__main__":
    _main()
