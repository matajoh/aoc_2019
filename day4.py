""" Solution to day 4 """

import pytest


def check_number(number):
    """ Checks whether the digits are monotonically increasing,
    and whether at least one digit is doubled.
    """
    digits = str(number)
    if len(digits) != 6:
        return False

    double = False
    last = '0'
    for digit in digits:
        if digit < last:
            return False

        if digit == last:
            double = True

        last = digit

    return double


def check_number_double(number):
    """ Check whether the digits increase monitonically, and if a digit
    repeats exactly twice.
    """
    digits = str(number)
    if len(digits) != 6:
        return False

    double = False
    last = '0'
    num_same = 0
    for digit in digits:
        if digit < last:
            return False

        if digit > last:
            if num_same == 2:
                double = True

            num_same = 0
        else:
            if num_same == 0:
                num_same = 2
            else:
                num_same += 1

        last = digit

    if num_same == 2:
        double = True

    return double


@pytest.mark.parametrize("number, expected", [
    (111111, True),
    (223450, False),
    (123789, False)
])
def test_check_number(number, expected):
    """ Test """
    actual = check_number(number)
    assert actual == expected


@pytest.mark.parametrize("number, expected", [
    (112233, True),
    (123444, False),
    (111122, True)
])
def test_check_number_double(number, expected):
    """ Test """
    actual = check_number_double(number)
    assert actual == expected


def count_in_range(start, end, check):
    """ Count how many values in the range pass the check """
    count = 0
    for val in range(start, end):
        if check(val):
            count += 1

    return count


def _main():
    print("part1: ", count_in_range(178416, 676461, check_number))
    print("part2: ", count_in_range(178416, 676461, check_number_double))


if __name__ == "__main__":
    _main()
