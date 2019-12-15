""" Solution for Day 8 """

import numpy as np

from common import asset


def parse_image(text: str, rows: int, cols: int) -> np.ndarray:
    """ Parse an image from the text string

    Args:
        text: a string of digits from 0-9
        rows: the number of rows per layer
        cols: the number of columns per layer

    Returns:
        a (N, rows, cols) np.uint8 tensor
    """
    digits = np.fromstring(text, dtype=np.uint8) - ord('0')
    return digits.reshape(-1, rows, cols)


def count_by_layer(image: np.ndarray, value: int, layer: int = None) -> np.ndarray:
    """ Count the number of values by layer.

    Args:
        image: the image
        value: the value to test

    Keyword Args:
        layer: specify a specific layer to count

    Returns:
        either an array of counts per layer, or a scalar (if layer was specified)
    """
    if layer is not None:
        return np.sum(image[layer] == value)

    return np.sum(image == value, axis=(1, 2))


def collapse(image: np.array) -> np.ndarray:
    """ Collapse the layers of an image following the transparency rules """
    output = np.zeros(image.shape[1:], np.uint8)
    image = image.transpose(1, 2, 0)
    for row in range(output.shape[0]):
        for col in range(output.shape[1]):
            index = np.argmax(image[row, col] != 2)
            output[row, col] = image[row, col, index]

    return output


def _main():
    with open(asset("day8.txt")) as file:
        image = parse_image(file.read(), 6, 25)

    max_zero_row = np.argmin(count_by_layer(image, 0))
    num_ones = count_by_layer(image, 1, max_zero_row)
    num_twos = count_by_layer(image, 2, max_zero_row)
    print("Part 1:", num_ones*num_twos)

    image = collapse(image)
    print("Part 2:")
    for line in image:
        print("".join(['#' if value else '.' for value in line]))


if __name__ == "__main__":
    _main()
