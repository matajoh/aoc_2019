from copy import copy

import numpy as np
import pytest


class MathOp:
    def __init__(self, code, operation):
        self._code = code
        self._operation = operation
    
    @property
    def code(self):
        return self._code

    def __call__(self, memory, counter):
        assert memory[counter] == self.code
        lhs = memory[counter+1]
        rhs = memory[counter+2]
        output = memory[counter+3]
        memory[output] = self._operation(memory[lhs], memory[rhs])
        return counter + 4


class Computer:
    def __init__(self, memory):
        self._memory = memory
        self._halt = 99
        self._ops = {
            op.code: op for op in [
                MathOp(1, lambda lhs, rhs: lhs + rhs),
                MathOp(2, lambda lhs, rhs: lhs * rhs)
            ]
        }

    def run(self, noun=None, verb=None):
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
                raise NotImplementedError("Unknown opcode {} at pc {}".format(opcode, counter))
        
        return memory


@pytest.mark.parametrize("input_memory, output_memory", [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2,3,0,3,99], [2,3,0,6,99]),
    ([2,4,4,5,99,0], [2,4,4,5,99,9801]),
    ([1,1,1,4,99,5,6,0,99], [30,1,1,4,2,5,6,0,99]),
    ([1,9,10,3,2,3,11,0,99,30,40,50], [3500,9,10,70,2,3,11,0,99,30,40,50])
])
def test_computer(input_memory, output_memory):
    computer = Computer(input_memory)
    np.testing.assert_array_equal(computer.run(), output_memory)
