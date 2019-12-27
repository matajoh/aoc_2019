""" Solution to Day 25 """

from common import asset
from intcode import Computer


def _main():
    with open(asset("day25.txt")) as file:
        program = [int(part) for part in file.read().split(',')]

    computer = Computer(program)
    commands = [
        "south",
        "take mouse",
        "north",
        "west",
        "north",
        "north",
        "north",
        "west",
        "take semiconductor",
        "east",
        "south",
        "west",
        "south",
        "take hypercube",
        "north",
        "east",
        "south",
        "west",
        "take antenna",
        "west",
        "south",
        "south",
        "south"
    ]

    computer.write_ascii("\n".join(commands) + '\n')
    while not computer.is_halted:
        while not computer.num_outputs and not computer.is_halted:
            computer.step()

        if computer.num_outputs:
            computer.print_ascii()


if __name__ == "__main__":
    _main()
