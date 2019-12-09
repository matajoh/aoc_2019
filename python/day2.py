""" Solution to Day 2 """

import os

from intcode import Computer


def _part1(program):
    computer = Computer(program)
    computer.run(12, 2)
    print("part1:", computer.memory[0])


def _part2(program, target):
    computer = Computer(program)
    for noun in range(100):
        for verb in range(100):
            computer.run(noun, verb)
            if computer.memory[0] == target:
                print("part2:", noun*100 + verb)
                return

    raise ValueError("Unable to find a valid noun/verb")


def _main():
    with open(os.path.join("..", "inputs", "day2.txt")) as file:
        program = [int(value) for value in file.read().split(',')]

    _part1(program)
    _part2(program, 19690720)


if __name__ == "__main__":
    _main()
