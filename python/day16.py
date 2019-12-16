import itertools
import sys
import time

import numpy as np
import pytest

from common import asset


def _compute_output(signal, index):
    output = 0
    num_repeats = index + 1
    pattern = [0, 1, 0, -1]
    current = 0
    count = num_repeats
    for i, val in enumerate(signal[index:]):
        if count == num_repeats:
            current = (current+1)%4
            count = 0
        
        mult = pattern[current]
        output += val*mult
        count += 1
    
    return abs(output) % 10
    

def _fft_step(input_signal, output_signal):
    signal_length = len(input_signal)
    for i in range(signal_length):
        output_signal[i] = _compute_output(input_signal, i)


def fft(signal, num_steps):
    input_signal = [ord(char) - ord('0') for char in signal]
    output_signal = [0]*len(signal)
    start = time.time()
    for _ in range(num_steps):
        _fft_step(input_signal, output_signal)
        input_signal, output_signal = output_signal, input_signal
        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\n')    
    print("Time per step:", (time.time() - start)/100)
    return input_signal


@pytest.mark.parametrize("signal, expected, num_steps", [
    ("12345678", "01029498", 4),
    ("80871224585914546619083218645595", "24176176", 100),
    ("19617804207202209144916044189917", "73745418", 100),
    ("69317163492948606335995924319873", "52432133", 100)
])
def test_fft(signal, expected, num_steps):
    signal = fft(signal, num_steps)
    signal = "".join([str(val) for val in signal[:8]])
    assert signal == expected


@pytest.mark.parametrize("signal, expected", [
    ("03036732577212944063491565474664", "84462026"),
    ("02935109699940807407585447034323", "78725270"),
    ("03081770884921959731165446850517", "53553731")
])
def test_fft2(signal, expected):
    offset = int(signal[:7])
    signal = fft(signal*10000, 100)
    assert signal[offset:offset+8] == expected


def _main():
    with open(asset("day16.txt")) as file:
        original_signal = file.read()

    signal = fft(original_signal, 100)
    signal = "".join([str(val) for val in signal[:8]])
    print("Part 1:", signal)

    original_signal = "03036732577212944063491565474664"
    signal = fft(original_signal*10000, 100)
    offset = int(original_signal[:7])
    signal = "".join([str(val) for val in signal[offset:offset+8]])
    print("Part 2:", signal)


if __name__ == "__main__":
    _main()
