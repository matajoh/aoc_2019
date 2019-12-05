""" Solution to Day 2 """

import os

from intcode import Computer


def _main():
    with open(os.path.join("inputs", "day5.txt")) as file:
        memory = [int(value) for value in file.read().split(',')]

    computer = Computer(memory)

    print("Part 1:")
    computer.run()

    print("Part 2:")
    computer.run()


if __name__ == "__main__":
    _main()
