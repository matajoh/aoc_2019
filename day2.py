import os
from copy import copy

import numpy as np
import pytest

from intcode import Computer


def part1(memory):
    computer = Computer(memory)
    memory = computer.run(12, 2)
    print("part1:", memory[0])


def part2(memory, target):
    computer = Computer(memory)
    for noun in range(100):
        for verb in range(100):
            memory = computer.run(noun, verb)
            if memory[0] == target:
                print("part2:", noun*100 + verb)
                return
    
    raise ValueError("Unable to find a valid noun/verb")


def _main():
    with open(os.path.join("inputs", "day2.txt")) as file:
        memory = [int(value) for value in file.read().split(',')]
    
    part1(copy(memory))
    part2(memory, 19690720)


if __name__ == "__main__":
    _main()
