import pytest

from common import read_tests, asset


class Deck:
    def __init__(self, num_cards):
        self.cards = None
        self._temp = None
        self._num_cards = num_cards
    
    def reset(self):
        self.cards = list(range(self._num_cards))
        self._temp = [0]*self._num_cards
    
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
            self._temp[(i*n)%self._num_cards] = card
        
        self.cards, self._temp = self._temp, self.cards
        return self.cards
    
    def shuffle(self, lines):
        if self.cards is None:
            self.reset()

        for line in lines:
            if line.startswith("deal into new stack"):
                self.deal_into_new_stack()
            elif line.startswith("cut"):
                n = int(line[4:])
                self.cut(n)
            elif line.startswith("deal with increment"):
                n = int(line[20:])
                self.deal_with_increment(n)
            else:
                raise ValueError("Unknown shuffle: " + line)
    
    def undo_shuffle(self, lines, index):
        lines = list(lines)
        if not lines:
            return index
        
        line = lines.pop()
        if line.startswith("deal into new stack"):
            index = self._num_cards-index-1
            return self.undo_shuffle(lines, index)
        
        if line.startswith("cut"):
            n = int(line[4:])
            return self.undo_shuffle(lines, (index + n) % self._num_cards)
        
        if line.startswith("deal with increment"):
            n = int(line[20:])
            mod = self._num_cards % n
            num = self._num_cards // n
            initial = [0]*n
            i = 0
            offset = 0
            for _ in range(n):
                initial[i] = offset
                if i < mod:
                    offset += 1
                
                i -= mod
                if i < 0:
                    i += n
                
                offset += num

            mod = index % n
            num = index // n
            return self.undo_shuffle(lines, initial[mod] + num)

        raise ValueError("Unknown shuffle: " + line)
        

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
    deck.shuffle(lines)
    actual = " ".join([str(card) for card in deck.cards])
    assert actual == expected

    values = [int(val) for val in expected.split()]
    for i, expected in enumerate(values):
        actual = deck.undo_shuffle(lines, i)
        assert actual == expected, "{} != {} at index {}".format(actual, expected, i)


def find_period(num_cards, shuffle):
    deck = Deck(num_cards)
    deck.reset()
    shuffle(deck)
    test = sum(card == 0 for card in deck.cards)
    if test > 1:
        raise ValueError("Invalid deck/shuffle combination")

    original_order = list(range(num_cards))
    period = 1
    for i in range(100):
        if deck.cards == original_order:
            break

        shuffle(deck)
        period += 1
    
    if period == 101:
        raise ValueError("Period not found")

    return period      


def _main():
    with open(asset("day22.txt")) as file:
        lines = list(file)
    
    
    deck = Deck(10007)
    deck.shuffle(lines)
    print("Part 1:", deck.cards.index(2019))

    #deck = Deck(119315717514047)
    
    num_shuffles = 101741582076661
    index = num_shuffles % period
    print(index)


def _explore(name, arg, start=10, end=100):
    if name == "cut":
        shuffle = lambda deck: deck.cut(arg)
    elif name == "inc":
        shuffle = lambda deck: deck.deal_with_increment(arg)
    elif name == "test":
        lines = read_tests("day22_tests.txt")
        shuffle = lambda deck: deck.shuffle(lines[arg])
    elif name == "raw":
        shuffle = lambda deck: deck.shuffle(arg)
    else:
        raise ValueError("Unknown shuffle" + name)

    points = []
    for num_cards in range(start, end):
        try:
            period = find_period(num_cards, shuffle)
            print(num_cards, period)
            points.append((num_cards, period))
        except ValueError:
            points.append((num_cards, -1))

    return points


def _write_csv(name, data):
    import csv

    with open(name, "w", newline="") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)


def _find_equiv(num_cards=10):
    import itertools
    deck = Deck(num_cards)

    commands = ["deal into new stack"]
    commands.extend(["deal with increment {}".format(i) for i in set([3, 7, 9, 21, 27, num_cards - 3, num_cards - 7])])
    commands.extend(["cut {}".format(i) for i in range(1, num_cards)])

    shuffles = list(itertools.permutations(commands, 2))
    for shuffle in shuffles:
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
        



   
if __name__ == "__main__":
    """
    strategy:

    1. Reduce the shuffle into a single cut and a single deal (should be possible with rules)
        a. remove all reverses
        b. group all cuts and steps together
        c. collapse
    2. Determine the period of the reduced shuffle (hopefully this is much easier!)
    3. ...
    4. Solution
    """
    _find_equiv()

