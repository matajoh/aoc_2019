""" Solution to Day 2 """

from intcode import Computer
from common import asset


def _part1(program):
    computer = Computer(program)
    computer.run(12, 2)
    print("Part 1:", computer.memory[0])


def _search_noun(computer, start, end, target):
    while end != start + 1:
        mid = (start + end) // 2
        computer.run(mid, 0)
        if computer.memory[0] <= target:
            start = mid
        else:
            end = mid

    return start


def _search_verb(computer, noun, start, end, target):
    while end != start + 1:
        mid = (start + end) // 2
        computer.run(noun, mid)
        if computer.memory[0] <= target:
            start = mid
        else:
            end = mid

    return start


def _part2(program, target):
    computer = Computer(program)
    noun = _search_noun(computer, 0, 100, target)
    verb = _search_verb(computer, noun, 0, 100, target)
    computer.run(noun, verb)
    assert computer.memory[0] == target
    print("Part 2:", noun*100 + verb)


def _main():
    with open(asset("day2.txt")) as file:
        program = [int(value) for value in file.read().split(',')]

    _part1(program)
    _part2(program, 19690720)


if __name__ == "__main__":
    _main()
