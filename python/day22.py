""" Solution to Day 22 """

from enum import Enum
from collections import namedtuple

import pytest

from common import read_tests, asset

#pylint: disable=redefined-outer-name


class ShuffleType(Enum):
    """ Different types of shuffles """
    Reverse = 0
    Cut = 1
    Increment = 2


class Shuffle(namedtuple("Shuffle", ["type", "arg"])):
    """ Represents a shuffle of the deck """
    @staticmethod
    def parse(line):
        """ Parse a shuffle from the line """
        if "new stack" in line:
            return Shuffle.rev()

        if "cut" in line:
            return Shuffle.cut(int(line[4:]))

        if "increment" in line:
            return Shuffle.inc(int(line[20:]))

        raise ValueError("Invalid shuffle")

    @staticmethod
    def rev():
        """ Creates a deal into new stack shuffle """
        return Shuffle(ShuffleType.Reverse, None)

    @staticmethod
    def cut(arg):
        """ Creates a cut shuffle """
        return Shuffle(ShuffleType.Cut, arg)

    @staticmethod
    def inc(arg):
        """ Creates a deal with increment shuffle """
        return Shuffle(ShuffleType.Increment, arg)

    @property
    def is_inc(self):
        """ Whether this is a deal with increment shuffle """
        return self.type == ShuffleType.Increment

    @property
    def is_rev(self):
        """ Whether this is a deal into new stack shuffle """
        return self.type == ShuffleType.Reverse

    @property
    def is_cut(self):
        """ Whether this is a cut shuffle """
        return self.type == ShuffleType.Cut

    def __repr__(self):
        if self.type == ShuffleType.Reverse:
            return "rev"

        if self.type == ShuffleType.Cut:
            return "cut({})".format(self.arg)

        if self.type == ShuffleType.Increment:
            return "inc({})".format(self.arg)

        raise ValueError("Invalid shuffle")


class Deck:
    """ Represents a deck of space cards """

    def __init__(self, num_cards):
        self.cards = None
        self._temp = None
        self.num_cards = num_cards

    def reset(self):
        """ Resets the deck to factory order """
        self.cards = list(range(self.num_cards))
        self._temp = [0]*self.num_cards

    def deal_into_new_stack(self):
        """ Deals the deck into a new stack """
        self.cards.reverse()
        return self.cards

    def cut(self, n):
        """ Cuts the deck """
        self._temp[:-n] = self.cards[n:]
        self._temp[-n:] = self.cards[:n]
        self.cards, self._temp = self._temp, self.cards
        return self.cards

    def deal_with_increment(self, n):
        """ Deals the deck with an increment """
        for i, card in enumerate(self.cards):
            self._temp[(i*n) % self.num_cards] = card

        self.cards, self._temp = self._temp, self.cards
        return self.cards

    def shuffle(self, shuffles):
        """ Applies the shuffles to the deck in order """
        if self.cards is None:
            self.reset()

        for shuffle in shuffles:
            if shuffle.type == ShuffleType.Reverse:
                self.deal_into_new_stack()
            elif shuffle.type == ShuffleType.Cut:
                self.cut(shuffle.arg)
            else:
                self.deal_with_increment(shuffle.arg)

    @staticmethod
    def _mod_inv(x, n):
        """ Returns the modulo inverse using Fermat's little theorem """
        return pow(x, n-2, n)

    def _index_transform(self, shuffles, num_repeats):
        """ Computes an index transform that determines where a card will
            be in the deck after a number of repeats of the stack of
            shuffles
        """
        shuffles = self.optimize(shuffles)
        # shuffles is now just an "inc x cut y" pair
        a = shuffles[0].arg
        b = self.num_cards-shuffles[1].arg

        # we can compute the position of a card now as
        # a*card + b
        # but now we must do this num_repeats times.
        # This expands into:
        # a^n + b*(\sum_k^M-13 a^k) mod N
        # where M is the number of repeats and N
        # is the number of cards in the deck.
        # We can collapse the sum into:
        # \frac{a^M - 1}{(a - 1)}
        # using Fermat's little theorem to compute
        # the inverse

        a_n = pow(a, num_repeats, self.num_cards)
        b_n = b * (a_n - 1) * self._mod_inv(a - 1, self.num_cards)
        return a_n, b_n

    def card_after_shuffle(self, shuffles, num_repeats, index):
        """ Return the card at an index after a number of shuffles """
        a, b = self._index_transform(shuffles, num_repeats)
        val = (index - b)*self._mod_inv(a, self.num_cards)
        return val % self.num_cards

    def index_after_shuffle(self, shuffles, num_repeats, card):
        """ Return the index of a card after a number of shuffles """
        a, b = self._index_transform(shuffles, num_repeats)
        return (a*card + b) % self.num_cards

    def optimize(self, shuffles):
        """ Optimizes a list of shuffles into a minimal form
            of a single deal with increment followed by a cut.
        """
        inc, cut = 1, 0
        for shuffle in shuffles:
            if shuffle.type == ShuffleType.Reverse:
                # each reverse is equivalent to
                # 1. deal with increment (N - 1)
                # 2. cut 1
                inc_i = - 1
                cut_i = 1
            elif shuffle.type == ShuffleType.Increment:
                inc_i = shuffle.arg
                cut_i = 0
            elif shuffle.type == ShuffleType.Cut:
                inc_i = 1
                cut_i = shuffle.arg
            else:
                raise ValueError("Unsupported shuffle")

            # we concatenate the new inc, cut to get
            # inc x, cut y, inc xi, cut yi
            # we then swap the inner cut and inc
            # which results in
            # inc x, inc xi, cut xi*y, cut yi
            # and then we combine
            # inc x*xi, cut xi*y + yi
            inc = (inc * inc_i) % self.num_cards
            cut = (inc_i * cut + cut_i) % self.num_cards

        if inc == 1 and cut == 0:
            return []

        if inc == 1:
            return [Shuffle.cut(cut)]

        if cut == 0:
            return [Shuffle.inc(inc)]

        return [Shuffle.inc(inc), Shuffle.cut(cut)]


@pytest.fixture(scope="module")
def tests():
    """ Fixture """
    return read_tests("day22_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, "0 3 6 9 2 5 8 1 4 7"),
    (1, "3 0 7 4 1 8 5 2 9 6"),
    (2, "6 3 0 7 4 1 8 5 2 9"),
    (3, "9 2 5 8 1 4 7 0 3 6")
])
def test_shuffle(tests, index, expected):
    """ Test """
    deck = Deck(10)
    lines = tests[index]
    shuffles = [Shuffle.parse(line) for line in lines]
    deck.shuffle(shuffles)
    actual = " ".join([str(card) for card in deck.cards])
    assert actual == expected


@pytest.mark.parametrize("index, expected", [
    (0, "0 3 6 9 2 5 8 1 4 7"),
    (1, "3 0 7 4 1 8 5 2 9 6"),
    (2, "6 3 0 7 4 1 8 5 2 9"),
    (3, "9 2 5 8 1 4 7 0 3 6")
])
def test_optimize(tests, index, expected):
    """ Test """
    deck = Deck(10)
    lines = tests[index]
    shuffles = [Shuffle.parse(line) for line in lines]
    shuffles = deck.optimize(shuffles)
    deck.shuffle(shuffles)
    actual = " ".join([str(card) for card in deck.cards])
    assert actual == expected


def _main():
    with open(asset("day22.txt")) as file:
        shuffles = [Shuffle.parse(line) for line in file]

    deck = Deck(10007)
    print("Part 1:", deck.index_after_shuffle(shuffles, 1, 2019))

    deck = Deck(119315717514047)
    print("Part 2:", deck.card_after_shuffle(shuffles, 101741582076661, 2020))


if __name__ == "__main__":
    _main()
