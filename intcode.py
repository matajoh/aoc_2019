""" Module providing an implementation of the Intcode computer """

from copy import copy
from typing import Callable, List

import numpy as np
import pytest


class MathOp:
    """ A basic math operation with four values

    Args:
        code: the op code
        operation: the callable operation, which must take two integers
                   and return an integer.
    """

    def __init__(self, code: int, operation: Callable[[int, int], int]):
        self._code = code
        self._operation = operation

    @property
    def code(self) -> int:
        """ The op code """
        return self._code

    def __call__(self, memory: List[int], counter: int) -> int:
        assert memory[counter] == self.code
        lhs = memory[counter+1]
        rhs = memory[counter+2]
        output = memory[counter+3]
        memory[output] = self._operation(memory[lhs], memory[rhs])
        return counter + 4


class Computer:
    """ An implementation of the Intcode computer.

    Args:
        memory: the initial memory. Will not be modified.
    """

    def __init__(self, memory: List[int]):
        self._memory = memory
        self._halt = 99
        self._ops = {
            op.code: op for op in [
                MathOp(1, lambda lhs, rhs: lhs + rhs),
                MathOp(2, lambda lhs, rhs: lhs * rhs)
            ]
        }

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
        while memory[counter] != self._halt:
            opcode = memory[counter]
            if opcode in self._ops:
                counter = self._ops[opcode](memory, counter)
            else:
                raise NotImplementedError(
                    "Unknown opcode {} at pc {}".format(opcode, counter))

        return memory


@pytest.mark.parametrize("input_memory, output_memory", [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50])
])
def test_computer(input_memory, output_memory):
    """ Test """
    computer = Computer(input_memory)
    np.testing.assert_array_equal(computer.run(), output_memory)