""" Solution to Day 7 """

import os
import itertools

import pytest

from intcode import Computer


def _feedback(program, settings):
    computers = [Computer(program) for _ in settings]

    for computer, setting in zip(computers, settings):
        computer.write(setting)

    value = 0
    computers[0].write(0)
    all_halted = False
    while not all_halted:
        all_halted = True
        for i, computer in enumerate(computers):
            if not (computer.needs_input or computer.is_halted):
                all_halted = False
                computer.step()
                if computer.has_output:
                    if i + 1 < len(computers):
                        computers[i+1].write(computer.read())
                    else:
                        value = computer.read()
                        computers[0].write(value)

    return value


@pytest.mark.parametrize("program, settings, expected", [
    ([3, 26, 1001, 26, -4, 26, 3, 27, 1002, 27, 2, 27, 1, 27, 26,
      27, 4, 27, 1001, 28, -1, 28, 1005, 28, 6, 99, 0, 0, 5],
     [9, 8, 7, 6, 5], 139629729),
    ([3, 52, 1001, 52, -5, 52, 3, 53, 1, 52, 56, 54, 1007, 54, 5, 55, 1005, 55, 26, 1001, 54,
      -5, 54, 1105, 1, 12, 1, 53, 54, 53, 1008, 54, 0, 55, 1001, 55, 1, 55, 2, 53, 55, 53, 4,
      53, 1001, 56, -1, 56, 1005, 56, 6, 99, 0, 0, 0, 0, 10], [9, 7, 8, 5, 6], 18216)
])
def test_feedback(program, settings, expected):
    """ Test the feedback amplifier configuration """
    assert _feedback(program, settings) == expected


def _part1(program, verbose=False):
    max_value = 0
    for settings in itertools.permutations([0, 1, 2, 3, 4]):
        value = 0
        for setting in settings:
            computer = Computer(program)
            computer.run(inputs=[setting, value])
            value = computer.read()

        if value > max_value:
            if verbose:
                print("new max:", settings, value)

            max_value = value

    print("Part 1:", max_value)


def _part2(program, verbose=False):
    max_value = 0
    for settings in itertools.permutations([5, 6, 7, 8, 9]):
        value = _feedback(program, settings)
        if value > max_value:
            if verbose:
                print("new max:", settings, value)

            max_value = value

    print("Part 2:", max_value)


def _main():
    with open(os.path.join("inputs", "day7.txt")) as file:
        program = [int(value) for value in file.read().split(',')]

    _part1(program)
    _part2(program)


if __name__ == "__main__":
    _main()
