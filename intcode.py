""" Module providing an implementation of the Intcode computer """

from copy import copy
from enum import IntEnum
from typing import List
from collections import namedtuple

import numpy as np
import pytest


class ParameterMode(IntEnum):
    """ Different modes for parameter interpretation """
    Position = 0    # Parameter is a memory position
    Immediate = 1   # Parameter is a literal value


def add(params: List[int], memory: List[int], counter: int) -> int:
    """ Adds two parameters and places them in an output position """
    lhs, rhs, output = params
    memory[output] = lhs + rhs
    return counter + 4


def multiply(params: List[int], memory: List[int], counter: int) -> int:
    """ Multiplies two parameters and places them in an output position """
    lhs, rhs, output = params
    memory[output] = lhs * rhs
    return counter + 4


def read_input(params: List[int], memory: List[int], counter: int) -> int:
    """ Reads input from the console """
    value = int(input("input> "))
    output, = params
    memory[output] = value
    return counter + 2


def write_output(params: List[int], _, counter: int) -> int:
    """ Writes output to the console """
    value, = params
    print("output>", value)
    return counter + 2


def jump_if_true(params: List[int], _, counter: int) -> int:
    """ Jumps the program counter if a condition is true """
    test, value = params
    if test:
        return value

    return counter + 3


def jump_if_false(params: List[int], _, counter: int) -> int:
    """ Jumps the program counter if a condition is false """
    test, value = params
    if test:
        return counter + 3

    return value


def less_than(params: List[int], memory: List[int], counter: int) -> int:
    """ Stores if one parameter is less than another """
    lhs, rhs, output = params
    memory[output] = 1 if lhs < rhs else 0
    return counter + 4


def equals(params: List[int], memory: List[int], counter: int) -> int:
    """ Stores if one parameter is greater than another """
    lhs, rhs, output = params
    memory[output] = 1 if lhs == rhs else 0
    return counter + 4


class Operation(namedtuple("Operation", ["call", "num_params", "num_outputs"])):
    """ Class encapsulating a computer operation """

    def modes(self, opcode):
        """ Extract the modes from the opcode """
        num_modes = self.num_params + self.num_outputs
        modes = [ParameterMode.Position]*num_modes
        opcode //= 100
        index = 0
        while opcode:
            if opcode % 10:
                modes[index] = ParameterMode.Immediate

            index += 1
            opcode //= 10

        if self.num_outputs:
            for mode in modes[-self.num_outputs:]:
                assert mode == ParameterMode.Position

        return modes

    def params(self, memory: List[int], counter: int) -> List[int]:
        """ Extract the parameters from memory """
        modes = self.modes(memory[counter])
        start = counter + 1
        end = start + self.num_params
        values = memory[start:end]
        params = []
        for mode, value in zip(modes, values):
            if mode == ParameterMode.Position:
                params.append(memory[value])
            else:
                params.append(value)

        start = end
        end = end + self.num_outputs

        return params + memory[start:end]

    def __call__(self, memory, counter):
        params = self.params(memory, counter)
        return self.call(params, memory, counter)


Operations = {
    1: Operation(add, 2, 1),
    2: Operation(multiply, 2, 1),
    3: Operation(read_input, 0, 1),
    4: Operation(write_output, 1, 0),
    5: Operation(jump_if_true, 2, 0),
    6: Operation(jump_if_false, 2, 0),
    7: Operation(less_than, 2, 1),
    8: Operation(equals, 2, 1),
    99: None
}


class Computer:
    """ An implementation of the Intcode computer.

    Args:
        memory: the initial memory. Will not be modified.
    """

    def __init__(self, memory: List[int]):
        self._memory = memory

    @property
    def memory(self) -> List[int]:
        """ The initial memory of the computer """
        return self._memory

    def run(self, noun: int = None, verb: int = None):
        """ Run the computer using the program loaded in its memory.

        Keyword Args:
            noun: an optional noun used to alter the program [None]
            verb: an optional verb used to alter the program [None]
        """
        memory = copy(self._memory)
        if noun is not None:
            memory[1] = noun

        if verb is not None:
            memory[2] = verb

        counter = 0
        while True:
            operation = Operations[memory[counter] % 100]
            if operation:
                counter = operation(memory, counter)
            else:
                break

        return memory


@pytest.mark.parametrize("input_memory, output_memory", [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]),
    ([1101, 100, -1, 4, 0], [1101, 100, -1, 4, 99])
])
def test_computer(input_memory, output_memory):
    """ Test """
    computer = Computer(input_memory)
    np.testing.assert_array_equal(computer.run(), output_memory)


@pytest.mark.parametrize("opcode, code, modes", [
    (1, 1, [0, 0, 0]),
    (2, 2, [0, 0, 0]),
    (3, 3, [0]),
    (4, 4, [0]),
    (1002, 2, [0, 1, 0]),
    (101, 1, [1, 0, 0]),
    (104, 4, [1]),
    (1101, 1, [1, 1, 0])
])
def test_operation(opcode, code, modes):
    """ Test the operation mode extraction """
    operation = Operations[code]
    np.testing.assert_array_equal(operation.modes(opcode), modes)
