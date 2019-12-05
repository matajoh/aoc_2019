""" Module providing an implementation of the Intcode computer """

from copy import copy
from enum import IntEnum
from typing import Callable, List
from collections import namedtuple

import numpy as np
import pytest


class ParameterMode(IntEnum):
    Position = 0
    Immediate = 1


def add(inst, memory, counter):
    lhs, rhs, output = inst.parameters(memory, counter)
    memory[output] = lhs + rhs
    return counter + 4

def multiply(inst, memory, counter):
    lhs, rhs, output = inst.parameters(memory, counter)
    memory[output] = lhs * rhs
    return counter + 4

def read_input(inst, memory, counter):
    value = int(input("input> "))
    output, = inst.parameters(memory, counter)
    memory[output] = value
    return counter + 2

def write_output(inst, memory, counter):
    value, = inst.parameters(memory, counter)
    print("output>", value)
    return counter + 2

def halt(inst, memory, counter):
    raise NotADirectoryError("Halt")

def jump_if_true(inst, memory, counter):
    test, value = inst.parameters(memory, counter)
    if test:
        return value
    
    return counter + 3

def jump_if_false(inst, memory, counter):
    test, value = inst.parameters(memory, counter)
    if test:
        return counter + 3
    
    return value

def less_than(inst, memory, counter):
    lhs, rhs, output = inst.parameters(memory, counter)
    memory[output] = 1 if lhs < rhs else 0
    return counter + 4

def equals(inst, memory, counter):
    lhs, rhs, output = inst.parameters(memory, counter)
    memory[output] = 1 if lhs == rhs else 0
    return counter + 4


Operation = namedtuple("Operation", ["call", "num_params", "num_outputs"])



class Instruction:
    MathCodes = [1, 2]
    Input = 3
    Output = 4
    Halt = 99

    Operations = {
        1: Operation(add, 2, 1),
        2: Operation(multiply, 2, 1),
        3: Operation(read_input, 0, 1),
        4: Operation(write_output, 1, 0),
        5: Operation(jump_if_true, 2, 0),
        6: Operation(jump_if_false, 2, 0),
        7: Operation(less_than, 2, 1),
        8: Operation(equals, 2, 1),
        99: Operation(halt, 0, 0)
    }

    def __init__(self, opcode):
        self.code = opcode % 100
        self.num_params = 0
        self.num_outputs = 0
        self.call, self.num_params, self.num_outputs = Instruction.Operations[self.code]

        num_modes = self.num_params + self.num_outputs
        modes = str(opcode).zfill(2 + num_modes)[:num_modes]
        self.modes = [ParameterMode(int(mode)) for mode in modes]
        self.modes = list(reversed(self.modes))
        if self.num_outputs:
            for mode in self.modes[-self.num_outputs:]:
                assert mode == ParameterMode.Position

    def parameters(self, memory, counter) -> List[int]:
        start = counter + 1
        end = start + self.num_params
        values = memory[start:end]
        params = []
        for mode, value in zip(self.modes, values):
            if mode == ParameterMode.Position:
                params.append(memory[value])
            else:
                params.append(value)

        start = end
        end = end + self.num_outputs
        params = params + memory[start:end]

        return params
    
    def __call__(self, memory, counter) -> int:
        return self.call(self, memory, counter)



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
            inst = Instruction(memory[counter])
            if inst.code == Instruction.Halt:
                break
            
            counter = inst(memory, counter)

        return memory


@pytest.mark.parametrize("input_memory, output_memory", [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]),
    ([1101,100,-1,4,0], [1101, 100, -1, 4, 99])
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
    (99, 99, []),
    (1002, 2, [0, 1, 0]),
    (101, 1, [1, 0, 0]),
    (104, 4, [1]),
    (1101, 1, [1, 1, 0])
])
def test_instruction(opcode, code, modes):
    inst = Instruction(opcode)
    assert inst.code == code
    np.testing.assert_array_equal(inst.modes, modes)
