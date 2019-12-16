import itertools
import sys
import time

import numpy as np
import pytest

from common import asset

def _compute_output_strided(input_signal, index):
    num_repeats = index + 1

    output = 0
    end = len(input_signal)
    pos_start = num_repeats - 1
    neg_start = pos_start + 2*num_repeats
    for i in range(num_repeats):
        pos = np.sum(input_signal[pos_start+i:end:num_repeats*4])
        neg = np.sum(input_signal[neg_start+i:end:num_repeats*4])
        output += pos - neg
    
    return abs(output)%10

def _compute_output_block(input_signal, index):
    pattern = [0, 1, 0, -1]
    current = 0
    num_repeats = index + 1
    output = 0
    signal_length = len(input_signal)
    count = num_repeats - 1
    start = 0
    while start < signal_length:
        if pattern[current] != 0:
            end = min(start + count, signal_length)
            val = np.sum(input_signal[start:end])
            output += pattern[current]*val
        
        start += count
        current = (current + 1)%4
        count = num_repeats
    
    return abs(output)%10


def _compute_output_optim(input_signal, index):
    assert index >= len(input_signal)//2
    output = np.sum(input_signal[index:])
    return abs(output)%10


def _fft_step(input_signal, output_signal, offset=0):
    signal_length = len(input_signal)
    half_length = signal_length // 2
    for i in range(offset, half_length):
        output_signal[i] = _compute_output_block(input_signal, i)
    
    output = 0
    start = signal_length - 1
    end = max(offset, half_length) - 1
    for i in range(start, end, -1):
        output += input_signal[i]
        output_signal[i] = abs(output)%10


def fft(signal, num_steps, use_offset=False):
    offset = int(signal[:7]) if use_offset else 0
    input_signal = np.frombuffer(signal.encode(), dtype=np.int8) - ord('0')
    output_signal = np.zeros_like(input_signal)
    for _ in range(num_steps):
        _fft_step(input_signal, output_signal, offset)
        input_signal, output_signal = output_signal, input_signal
        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\n')

    return "".join([str(val) for val in input_signal[offset:offset+8]])


@pytest.mark.parametrize("signal, expected, num_steps", [
    ("12345678", "01029498", 4),
    ("80871224585914546619083218645595", "24176176", 100),
    ("19617804207202209144916044189917", "73745418", 100),
    ("69317163492948606335995924319873", "52432133", 100)
])
def test_fft(signal, expected, num_steps):
    signal = fft(signal, num_steps)
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

    signal = fft(original_signal*10000, 100, True)
    print("Part 2:", signal)


if __name__ == "__main__":
    _main()
