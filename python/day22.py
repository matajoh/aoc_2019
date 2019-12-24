from enum import Enum
from collections import namedtuple

import pytest

from common import read_tests, asset, solveLinearCongruenceEquations


class ShuffleType(Enum):
    Reverse=0
    Cut=1
    Increment=2  


class Shuffle(namedtuple("Shuffle", ["type", "arg"])):
    @staticmethod
    def parse(line):
        if "new stack" in line:
            return Shuffle.rev()

        if "cut" in line:
            return Shuffle.cut(int(line[4:]))

        if "increment" in line:
            return Shuffle.inc(int(line[20:]))

        raise ValueError("Invalid shuffle")
    
    @staticmethod
    def rev():
        return Shuffle(ShuffleType.Reverse, None)
    
    @staticmethod
    def cut(arg):
        return Shuffle(ShuffleType.Cut, arg)
    
    @staticmethod
    def inc(arg):
        return Shuffle(ShuffleType.Increment, arg)
    
    def __repr__(self):
        if self.type == ShuffleType.Reverse:
            return "rev"
        
        if self.type == ShuffleType.Cut:
            return "cut({})".format(self.arg)
        
        if self.type == ShuffleType.Increment:
            return "inc({})".format(self.arg)
        
        raise ValueError("Invalid shuffle")


class Deck:
    def __init__(self, num_cards):
        self.cards = None
        self._temp = None
        self.num_cards = num_cards
    
    def reset(self):
        self.cards = list(range(self.num_cards))
        self._temp = [0]*self.num_cards
    
    def deal_into_new_stack(self):
        self.cards.reverse()
        return self.cards
    
    def cut(self, n):
        self._temp[:-n] = self.cards[n:]
        self._temp[-n:] = self.cards[:n]
        self.cards, self._temp = self._temp, self.cards
        return self.cards
    
    def deal_with_increment(self, n):
        for i, card in enumerate(self.cards):
            self._temp[(i*n)%self.num_cards] = card
        
        self.cards, self._temp = self._temp, self.cards
        return self.cards
    
    def increment_index(self, cut, inc):
        val = solveLinearCongruenceEquations([0, cut], [inc, self.num_cards])["congruence class"]
        return val // inc
    
    def shuffle(self, shuffles):
        if self.cards is None:
            self.reset()

        for shuffle in shuffles:
            if shuffle.type == ShuffleType.Reverse:
                self.deal_into_new_stack()
            elif shuffle.type == ShuffleType.Cut:
                self.cut(shuffle.arg)
            else:
                self.deal_with_increment(shuffle.arg)
    
    def combine(self, lhs, rhs):
        assert lhs.type == rhs.type
        if lhs.type == ShuffleType.Reverse:
            return []
        
        if lhs.type == ShuffleType.Cut:
            arg = (lhs.arg + rhs.arg)%self.num_cards
            if arg == 0:
                return []
            
            return [Shuffle.cut(arg)]
        
        if lhs.type == ShuffleType.Increment:
            arg = (lhs.arg * rhs.arg) % self.num_cards
            if arg == 1:
                return []
            
            return [Shuffle.inc(arg)]
        
        raise ValueError("Unsupported shuffle type")

    def remove_reverse(self, lhs, rhs):
        assert lhs.type == ShuffleType.Reverse
        if rhs.type == ShuffleType.Cut:
            return [Shuffle.cut(self.num_cards - rhs.arg), Shuffle.rev()]
        
        if rhs.type == ShuffleType.Reverse:
            return []
        
        if rhs.type == ShuffleType.Increment:
            return [Shuffle.inc(self.num_cards - rhs.arg), Shuffle.cut(rhs.arg)]

        raise ValueError("Unsupported shuffle type")
    
    def swap(self, lhs, rhs):
        if lhs.type == ShuffleType.Increment:
            arg = self.increment_index(rhs.arg, lhs.arg)
            return [Shuffle.cut(arg), lhs]
        
        if lhs.type == ShuffleType.Cut:
            arg = (lhs.arg * rhs.arg)%self.num_cards
            return [rhs, Shuffle.cut(arg)]
        
        raise ValueError("Unsupported swap")

    def _optimize_step(self, shuffles):
        # remove doubles
        for i, (lhs, rhs) in enumerate(zip(shuffles[:-1], shuffles[1:])):
            if lhs.type == rhs.type:
                new_shuffles = shuffles[:i]
                new_shuffles.extend(self.combine(lhs, rhs))
                new_shuffles.extend(shuffles[i+2:])
                return new_shuffles
        
        # remove reverses
        for i, (lhs, rhs) in enumerate(zip(shuffles[:-1], shuffles[1:])):
            if lhs.type == ShuffleType.Reverse:
                new_shuffles = shuffles[:i]
                new_shuffles.extend(self.remove_reverse(lhs, rhs))
                new_shuffles.extend(shuffles[i+2:])
                return new_shuffles
           
        # create doubles
        for i, (lhs, rhs) in enumerate(zip(shuffles[:-2], shuffles[2:])):
            if lhs.type == rhs.type:
                new_shuffles = shuffles[:i]
                new_shuffles.extend(self.swap(lhs, shuffles[i+1]))
                new_shuffles.extend(shuffles[i+2:])
                return new_shuffles
        
        if len(shuffles) == 2 and shuffles[0].type == ShuffleType.Cut:
            return self.swap(*shuffles)
        
        return None
    
    def optimize(self, shuffles):
        new_shuffles = []
        for shuffle in shuffles:
            if shuffle.type == ShuffleType.Cut and shuffle.arg < 0:
                new_shuffles.append(Shuffle.cut(self.num_cards + shuffle.arg))
            else:
                new_shuffles.append(shuffle)
        
        shuffles = new_shuffles
        while True:
            new_shuffles = self._optimize_step(shuffles)
            if new_shuffles is None:
                return shuffles
            
            shuffles = new_shuffles

@pytest.fixture(scope="module")
def tests():
    return read_tests("day22_tests.txt")


@pytest.mark.parametrize("index, expected", [
    (0, "0 3 6 9 2 5 8 1 4 7"),
    (1, "3 0 7 4 1 8 5 2 9 6"),
    (2, "6 3 0 7 4 1 8 5 2 9"),
    (3, "9 2 5 8 1 4 7 0 3 6")
])
def test_shuffle(tests, index, expected):
    deck = Deck(10)
    lines = tests[index]
    shuffles = [Shuffle.parse(line) for line in lines]
    deck.shuffle(shuffles)
    actual = " ".join([str(card) for card in deck.cards])
    assert actual == expected

@pytest.mark.parametrize("num_cards", [10, 22, 40])
def test_increment_index(num_cards):
    deck = Deck(num_cards)
    for inc in [3, 7, 9]:
        deck.reset()
        deck.deal_with_increment(inc)

        for i, expected in enumerate(deck.cards):
            assert deck.increment_index(i, inc) == expected

@pytest.mark.parametrize("index, expected", [
    (0, "0 3 6 9 2 5 8 1 4 7"),
    (1, "3 0 7 4 1 8 5 2 9 6"),
    (2, "6 3 0 7 4 1 8 5 2 9"),
    (3, "9 2 5 8 1 4 7 0 3 6")
])
def test_optimize(tests, index, expected):
    deck = Deck(10)
    lines = tests[index]
    shuffles = [Shuffle.parse(line) for line in lines]
    shuffles = deck.optimize(shuffles)
    deck.shuffle(shuffles)
    actual = " ".join([str(card) for card in deck.cards])
    assert actual == expected


def _find_equiv(num_cards=10):
    import itertools
    deck = Deck(num_cards)

    commands = [Shuffle.rev()]
    commands.extend([Shuffle.inc(i) for i in set([3, 7, 9, 21, 27, num_cards - 3, num_cards - 7])])
    commands.extend([Shuffle.cut(i) for i in range(1, num_cards)])

    shuffles = list(itertools.permutations(commands, 2))
    for shuffle in shuffles:
        if not(shuffle[0].type == ShuffleType.Cut and
               shuffle[1].type == ShuffleType.Increment and
               shuffle[0].arg > shuffle[1].arg):
            continue

        deck.reset()
        deck.shuffle(shuffle)
        target = list(deck.cards)
        
        for singleton in commands:
            deck.reset()
            deck.shuffle([singleton])
            if deck.cards == target:
                print(shuffle, "=", singleton)
        
        for double in shuffles:
            if shuffle == double:
                continue

            deck.reset()
            deck.shuffle(double)
            if deck.cards == target:
                print(shuffle, "=", double)
        

def _main():
    with open(asset("day22.txt")) as file:
        lines = list(file)
    #lines = read_tests("day22_tests.txt")[3]

    shuffles = [Shuffle.parse(line) for line in lines]
    deck = Deck(119315717514047)
    optim = deck.optimize(shuffles)
    print(optim)
    shuffle = []
    period = None
    for i in range(deck.num_cards):
        #if i % 10000 == 0:
        print(i, shuffle)

        shuffle = shuffle + optim
        shuffle = deck.optimize(shuffle)
        if not shuffle:
            period = i + 1
            break

    if period is None:
        print("No period")
    else:
        print("Period:", period)
        deck.reset()
        for i in range(period):
            deck.shuffle(shuffles)
    


if __name__ == "__main__":
    _main()
