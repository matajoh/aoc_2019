""" Solution for day 12 """

#pylint: disable=redefined-outer-name

from collections import namedtuple
import itertools

import pytest
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import cnames #pylint: disable=unused-import
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D #pylint: disable=unused-import

from common import asset, read_tests, compute_lcm


class Vector(namedtuple("Vector", ["x", "y", "z"])):
    """ Class representing a 3D vector """

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def velocity(self, other: "Vector"):
        """ Computes the velocity with respect to another vector """
        return Vector(1 if self.x < other.x else (-1 if self.x > other.x else 0),
                      1 if self.y < other.y else (-1 if self.y >
                                                  other.y else 0),
                      1 if self.z < other.z else (-1 if self.z > other.z else 0))

    def __repr__(self) -> str:
        return "<x={}, y={}, z={}>".format(*self)

    def energy_repr(self) -> str:
        """ Returns a text representation of the energy calculation """
        vals = [abs(val) for val in self] + [self.energy]
        return "{} + {} + {} = {}".format(*vals)

    @property
    def energy(self) -> int:
        """ Compute the energy of the vector """
        return sum([abs(val) for val in self])

    @staticmethod
    def parse(line) -> "Vector":
        """ Parses a vector from text """
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
    """ Represents a sequence of values, which acts like a fixed-size queue """

    def __init__(self, values):
        self.values = values

    def add(self, value):
        """ Adds a value to the sequence, discarding the oldest to make room """
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
    """ Represents one of the simulated moons """

    def __init__(self, position: Vector):
        self.position = position
        self.velocity = Vector(0, 0, 0)

    def update_velocity(self, other: "Moon"):
        """ Updates the velocity of this moon with respect to the other moon """
        self.velocity += self.position.velocity(other.position)

    def update_position(self):
        """ Updates the position of the moon using its velocity """
        self.position += self.velocity

    @property
    def energy(self) -> int:
        """ Computes the total energy of the moon """
        return self.position.energy * self.velocity.energy

    def __repr__(self) -> str:
        return "pos={}, vel={}".format(self.position, self.velocity)

    def energy_repr(self) -> str:
        """ Returns a representation of the energy calculation """
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


def _do_step(moons):
    for moon0, moon1 in itertools.combinations(moons, 2):
        moon0.update_velocity(moon1)
        moon1.update_velocity(moon0)

    for moon in moons:
        moon.update_position()


def _simulate_movement(moons, steps, record=None):
    _print_state(0, moons)
    interval = steps // 10
    for step in range(steps):
        if record is not None:
            record.append([moon.position for moon in moons])

        _do_step(moons)

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


def _find_periods(moons, steps, num_samples=100):
    record = []
    _simulate_movement(moons, steps, record)

    num_moons = len(moons)

    selectors = []
    for i in range(num_moons):
        selectors.append(lambda state, i=i: state[i].x)
        selectors.append(lambda state, i=i: state[i].y)
        selectors.append(lambda state, i=i: state[i].z)

    periods = [0]*len(selectors)

    sequences = [Sequence([select(state) for state in record[:num_samples]])
                 for select in selectors]
    test_sequences = [Sequence([select(state) for state in record[:num_samples]])
                      for select in selectors]

    for i, state in enumerate(record[num_samples:]):
        for j, expected in enumerate(sequences):
            if test_sequences[j] == expected:
                if periods[j] == 0:
                    periods[j] = i

        for sequence, select in zip(test_sequences, selectors):
            sequence.add(select(state))

    return set(periods)


def _find_reset_time(moons, steps):
    periods = _find_periods(moons, steps)
    print("Unique periods:", periods)
    lcm = 1
    for period in periods:
        lcm = compute_lcm(lcm, period)

    return lcm


@pytest.fixture(scope="module")
def tests():
    """ Tests test fixture """
    return read_tests("day12_tests.txt")


@pytest.mark.parametrize("index, steps, expected", [
    (0, 10, 179),
    (1, 100, 1940)
])
def test_simulate_movement(tests, index, steps, expected):
    """ TEST """
    moons = [Moon(Vector.parse(line)) for line in tests[index]]

    assert _simulate_movement(moons, steps) == expected


@pytest.mark.parametrize("index, steps, expected", [
    (0, 5000, 2772),
    (1, 10000, 4686774924)
])
def test_find_reset_time(tests, index, steps, expected):
    """ TEST """
    moons = [Moon(Vector.parse(line)) for line in tests[index]]

    assert _find_reset_time(moons, steps) == expected


def _orbit_animation(moons, num_frames=500, mp4=False):
    frames = []
    for _ in range(num_frames):
        frames.append([moon.position for moon in moons])
        _do_step(moons)

    frames = np.array(frames)
    frames = frames.transpose(1, 0, 2)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    colors = plt.cm.jet(np.linspace(0, 1, len(moons))) #pylint: disable=no-member
    lines = sum([ax.plot([], [], [], '-', c=c)
                 for c in colors], [])
    pts = sum([ax.plot([], [], [], 'o', c=c, markersize=10)
               for c in colors], [])

    ax.set_xlim((-100, 100))
    ax.set_ylim((-100, 100))
    ax.set_zlim((-100, 100))

    ax.view_init(30, 0)

    def init():
        for line, pt in zip(lines, pts):
            line.set_data([], [])
            line.set_3d_properties([])

            pt.set_data([], [])
            pt.set_3d_properties([])

        return pts + lines

    def animate(i):
        for line, pt, frame in zip(lines, pts, frames):
            x, y, z = frame[:i].T

            line.set_data(x, y)
            line.set_3d_properties(z)

            pt.set_data(x[-1:], y[-1:])
            pt.set_3d_properties(z[-1:])

        ax.view_init(30, np.sin(i*.01)*45 + 45)
        fig.canvas.draw()
        return pts + lines

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=500, interval=30, blit=False)

    if mp4:
        anim.save('orbits.mp4', fps=15, extra_args=['-vcodec', 'libx264'])

    plt.show()


def _main():
    with open(asset("day12.txt")) as file:
        initial_state = [Vector.parse(line) for line in file]

    moons = [Moon(pos) for pos in initial_state]

    energy = _simulate_movement(moons, 1000)
    print("Part 1:", energy)

    reset_time = _find_reset_time(moons, 300000)
    print("Part 2:", reset_time)

    #moons = [Moon(pos) for pos in initial_state]
    #_orbit_animation(moons, mp4=True)


if __name__ == "__main__":
    _main()
