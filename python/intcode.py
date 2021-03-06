""" Module providing an implementation of the Intcode computer """

import sys
from enum import IntEnum
from typing import List, Mapping
from collections import namedtuple

import numpy as np
import pytest


class Memory:
    """ Class representing the memory of an Intcode computer """

    def __init__(self, values):
        self._lookup = dict(enumerate(values))

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = 0 if key.start is None else key.start
            stop = key.stop
            step = 1 if key.step is None else key.step
            return [self[i] for i in range(start, stop, step)]

        if key not in self._lookup:
            self._lookup[key] = 0

        return self._lookup[key]

    def __setitem__(self, key, value):
        self._lookup[key] = value

    def to_list(self) -> List[int]:
        """ Converts the memory to a list representation """
        start = 0
        stop = max(self._lookup.keys()) + 1
        return [self[i] for i in range(start, stop)]


class ParameterMode(IntEnum):
    """ Different modes for parameter interpretation """
    Position = 0    # Parameter is a memory position
    Immediate = 1   # Parameter is a literal value
    Relative = 2    # Parameter utilizes the relative base


class Operation(namedtuple("Operation", ["code", "call", "num_params", "num_outputs"])):
    """ Class encapsulating a computer operation """

    def modes(self, opcode):
        """ Extract the modes from the opcode """
        num_modes = self.num_params + self.num_outputs
        modes = [ParameterMode.Position]*num_modes
        opcode //= 100
        index = 0
        while opcode:
            mode = opcode % 10
            if mode == 1:
                modes[index] = ParameterMode.Immediate
            elif mode == 2:
                modes[index] = ParameterMode.Relative

            index += 1
            opcode //= 10

        if self.num_outputs:
            for mode in modes[-self.num_outputs:]:
                assert mode in (ParameterMode.Position, ParameterMode.Relative)

        return modes

    def params(self, memory: Memory, counter: int, relative_base: int) -> List[int]:
        """ Extract the parameters from memory """
        modes = self.modes(memory[counter])
        start = counter + 1
        end = start + self.num_params + self.num_outputs
        values = memory[start:end]
        params = []
        for mode, value in zip(modes, values):
            if mode == ParameterMode.Position:
                params.append(value)
            elif mode == ParameterMode.Relative:
                params.append(value + relative_base)
            else:
                params.append(value)

        for i in range(self.num_params):
            if modes[i] != ParameterMode.Immediate:
                params[i] = memory[params[i]]

        return params

    def __call__(self, memory, counter, relative_base):
        params = self.params(memory, counter, relative_base)
        return self.call(params, memory, counter)


class Computer:
    """ An implementation of the Intcode computer.

    Args:
        memory: the initial memory. Will not be modified.
    """

    def __init__(self, memory: Memory, verbose=False):
        self._initial_memory = memory.copy()
        self._memory = Memory(memory)
        self._verbose = verbose
        self._counter = 0
        self._relative_base = 0
        self._inputs = []
        self._outputs = []
        self._ops = {
            1: Operation(1, self.add, 2, 1),
            2: Operation(2, self.multiply, 2, 1),
            3: Operation(3, self.input, 0, 1),
            4: Operation(4, self.output, 1, 0),
            5: Operation(5, self.jump_if_true, 2, 0),
            6: Operation(6, self.jump_if_false, 2, 0),
            7: Operation(7, self.less_than, 2, 1),
            8: Operation(8, self.equals, 2, 1),
            9: Operation(9, self.relative_base_offset, 1, 0),
            99: None
        }

    def print_ascii(self):
        """ Print all of the output to the console """
        while self.num_outputs:
            val = self.read()
            if val < 255:
                sys.stdout.write(chr(val))
            else:
                return val

        return None

    def write_ascii(self, chars):
        """ Write all of the ASCII characters to the computer input """
        for char in chars:
            self.write(ord(char))
            sys.stdout.write(char)

    def reset(self):
        """ Reset the computer """
        self._memory = Memory(self._initial_memory)
        self._inputs.clear()
        self._outputs.clear()
        self._counter = 0
        self._relative_base = 0

    def run_to_input(self):
        """ Run until the computer requests input """
        while not self.needs_input:
            self.step()

    def run_to_output(self):
        """ Run until the computer produces an output """
        while not self.num_outputs:
            self.step()

    def clear_output(self):
        """ Clear the outputs """
        self._outputs.clear()

    @property
    def memory(self) -> List[int]:
        """ The memory of the computer """
        return self._memory.to_list()

    @property
    def ops(self) -> Mapping[int, Operation]:
        """ The operations of the computer """
        return self._ops

    def write(self, value: int):
        """ Write to the input buffer of the computer """
        self._inputs.append(value)

    def read(self) -> int:
        """ Read from the output buffer of the computer """
        return self._outputs.pop(0)

    @property
    def num_outputs(self) -> bool:
        """ Returns whether the computer has produced output """
        return len(self._outputs)

    @property
    def needs_input(self) -> bool:
        """ Returns whether the computer will read on its next iteration """
        opcode = self._memory[self._counter]
        return opcode % 100 == 3 and not self._inputs

    @property
    def is_halted(self) -> bool:
        """ Whether the computer is halted """
        opcode = self._memory[self._counter]
        return self._ops[opcode % 100] is None

    def step(self):
        """ Steps the computer forward by one instruction """
        opcode = self._memory[self._counter]
        operation = self._ops[opcode % 100]
        if operation:
            self._counter = operation(
                self._memory, self._counter, self._relative_base)

    def run(self, noun: int = None, verb: int = None, inputs: List[int] = None):
        """ Run the computer using the program loaded in its memory.

        Keyword Args:
            noun: an optional noun used to alter the program [None]
            verb: an optional verb used to alter the program [None]

        Returns:
            the outputs of the program
        """
        self.reset()
        if noun is not None:
            self._memory[1] = noun

        if verb is not None:
            self._memory[2] = verb

        if inputs:
            self._inputs = inputs
        else:
            self._inputs.clear()

        self._outputs.clear()

        while True:
            operation = self._ops[self._memory[self._counter] % 100]
            if operation:
                self._counter = operation(
                    self._memory, self._counter, self._relative_base)
            else:
                break

    @staticmethod
    def add(params: List[int], memory: Memory, counter: int) -> int:
        """ Adds two parameters and places them in an output position """
        lhs, rhs, output = params
        memory[output] = lhs + rhs
        return counter + 4

    @staticmethod
    def multiply(params: List[int], memory: Memory, counter: int) -> int:
        """ Multiplies two parameters and places them in an output position """
        lhs, rhs, output = params
        memory[output] = lhs * rhs
        return counter + 4

    def input(self, params: List[int], memory: Memory, counter: int) -> int:
        """ Reads input from the console """
        if self._inputs:
            value = self._inputs.pop(0)
            if self._verbose:
                print("input>", value)
        else:
            value = int(input("input> "))

        output, = params
        memory[output] = value
        return counter + 2

    def output(self, params: List[int], _, counter: int) -> int:
        """ Writes output to the console """
        value, = params
        self._outputs.append(value)
        if self._verbose:
            print("output>", value)

        return counter + 2

    @staticmethod
    def jump_if_true(params: List[int], _, counter: int) -> int:
        """ Jumps the program counter if a condition is true """
        test, value = params
        if test:
            return value

        return counter + 3

    @staticmethod
    def jump_if_false(params: List[int], _, counter: int) -> int:
        """ Jumps the program counter if a condition is false """
        test, value = params
        if test:
            return counter + 3

        return value

    @staticmethod
    def less_than(params: List[int], memory: Memory, counter: int) -> int:
        """ Stores if one parameter is less than another """
        lhs, rhs, output = params
        memory[output] = 1 if lhs < rhs else 0
        return counter + 4

    @staticmethod
    def equals(params: List[int], memory: Memory, counter: int) -> int:
        """ Stores if one parameter is greater than another """
        lhs, rhs, output = params
        memory[output] = 1 if lhs == rhs else 0
        return counter + 4

    def relative_base_offset(self, params: List[int], _, counter: int) -> int:
        """ Adjusts the relative base offset """
        offset, = params
        self._relative_base += offset
        return counter + 2


@pytest.mark.parametrize("input_memory, output_memory", [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]),
    ([1101, 100, -1, 4, 0], [1101, 100, -1, 4, 99]),
])
def test_memory(input_memory, output_memory):
    """ Test """
    computer = Computer(input_memory)
    computer.run()
    np.testing.assert_array_equal(computer.memory, output_memory)


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
    computer = Computer([])
    operation = computer.ops[code]
    np.testing.assert_array_equal(operation.modes(opcode), modes)


@pytest.mark.parametrize("program, settings, expected", [
    ([3, 15, 3, 16, 1002, 16, 10, 16, 1, 16, 15,
      15, 4, 15, 99, 0, 0], [4, 3, 2, 1, 0], 43210),
    ([3, 23, 3, 24, 1002, 24, 10, 24, 1002, 23, -1, 23, 101,
      5, 23, 23, 1, 24, 23, 23, 4, 23, 99, 0, 0],
     [0, 1, 2, 3, 4], 54321),
    ([3, 31, 3, 32, 1002, 32, 10, 32, 1001, 31, -2, 31, 1007, 31, 0, 33,
      1002, 33, 7, 33, 1, 33, 31, 31, 1, 32, 31, 31, 4, 31, 99, 0, 0, 0],
     [1, 0, 4, 3, 2], 65210)
])
def test_io(program, settings, expected):
    """ Tests the IO capabilities of the machine """
    actual = 0
    for setting in settings:
        computer = Computer(program)
        computer.run(inputs=[setting, actual])
        actual = computer.read()

    assert actual == expected


@pytest.mark.parametrize("program, expected", [
    ([109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99],
     [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]),
    ([1102, 34915192, 34915192, 7, 4, 7, 99, 0], [1219070632396864]),
    ([104, 1125899906842624, 99], [1125899906842624])
])
def test_outputs(program, expected):
    """ Tests programs by their output """
    computer = Computer(program)
    computer.run()
    actual = []
    while computer.num_outputs:
        actual.append(computer.read())

    np.testing.assert_array_equal(actual, expected)
