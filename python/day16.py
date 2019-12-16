""" Solution to Day 16 """

import sys

import pytest

from common import asset


def _compute_output_block(input_signal, index, offset):
    pattern = [0, 1, 0, -1]
    current = 0
    num_repeats = index + 1
    output = 0
    signal_length = len(input_signal)
    count = num_repeats - 1
    pos = 0
    while pos < signal_length:
        if pattern[current] != 0:
            start = pos - offset
            end = min(start + count, signal_length)
            val = sum(input_signal[start:end])
            output += pattern[current]*val

        pos += count
        current = (current + 1) % 4
        count = num_repeats

    return abs(output) % 10


def _fft_step(input_signal, output_signal, offset=0):
    signal_length = len(input_signal) + offset
    half_length = signal_length // 2
    for i in range(offset, half_length):
        output_signal[i] = _compute_output_block(input_signal, i, offset)

    output = 0
    start = signal_length - 1 - offset
    end = max(0, half_length-offset) - 1
    for i in range(start, end, -1):
        output += input_signal[i]
        output_signal[i] = abs(output) % 10


def _prep_signal(signal, offset, num_repeats):
    total_length = len(signal)*num_repeats
    length = total_length - offset
    num_complete = length // len(signal)
    signal *= num_complete
    diff = length - len(signal)
    if diff:
        signal = signal[-diff:] + signal

    zero = ord('0')
    return [ord(char) - zero for char in signal]


def fft(signal, num_steps, use_offset=False, num_repeats=1):
    """ Computes the Flawed Frequency Transmission algorithm """
    offset = int(signal[:7]) if use_offset else 0
    input_signal = _prep_signal(signal, offset, num_repeats)
    output_signal = [0]*len(input_signal)
    for _ in range(num_steps):
        _fft_step(input_signal, output_signal, offset)
        input_signal, output_signal = output_signal, input_signal
        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\n')

    return "".join([str(val) for val in input_signal[:8]])


@pytest.mark.parametrize("signal, expected, num_steps", [
    ("12345678", "01029498", 4),
    ("80871224585914546619083218645595", "24176176", 100),
    ("19617804207202209144916044189917", "73745418", 100),
    ("69317163492948606335995924319873", "52432133", 100)
])
def test_fft(signal, expected, num_steps):
    """ Test """
    signal = fft(signal, num_steps)
    assert signal == expected


@pytest.mark.parametrize("signal, expected", [
    ("03036732577212944063491565474664", "84462026"),
    ("02935109699940807407585447034323", "78725270"),
    ("03081770884921959731165446850517", "53553731")
])
def test_fft2(signal, expected):
    """ Test """
    signal = fft(signal, 100, True, 10000)
    assert signal == expected


def _main():
    with open(asset("day16.txt")) as file:
        original_signal = file.read()

    signal = fft(original_signal, 100)
    signal = "".join([str(val) for val in signal[:8]])
    print("Part 1:", signal)

    signal = fft(original_signal, 100, True, 10000)
    print("Part 2:", signal)


if __name__ == "__main__":
    _main()
