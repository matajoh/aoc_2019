""" Solution to day 21 """

from common import asset
from intcode import Computer

ASSEMBLER0 = """OR A T
AND B T
AND C T
NOT T J
AND D J
WALK
"""

ASSEMBLER1 = """OR A T
AND B T
AND C T
NOT T J
OR E T
OR H T
AND T J
AND D J
RUN
"""


def _run_assembler(program, assembler):
    computer = Computer(program)
    while not computer.needs_input:
        computer.step()

    computer.print_ascii()
    computer.write_ascii(assembler)

    while not computer.is_halted:
        computer.step()

    return computer.print_ascii()


def _main():
    with open(asset("day21.txt")) as file:
        program = [int(part) for part in file.read().split(',')]

    print("Part 1:", _run_assembler(program, ASSEMBLER0))

    print("Part 2:", _run_assembler(program, ASSEMBLER1))


if __name__ == "__main__":
    _main()
