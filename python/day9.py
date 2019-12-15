""" Solution to Day 9 """

from intcode import Computer
from common import asset


def _main():
    with open(asset("day9.txt")) as file:
        memory = [int(value) for value in file.read().split(',')]

    computer = Computer(memory, verbose=True)

    print("Part 1:")
    computer.run(inputs=[1])

    print("Part 2:")
    computer.run(inputs=[2])


if __name__ == "__main__":
    _main()
