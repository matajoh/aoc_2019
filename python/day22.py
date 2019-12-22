import pytest

from common import read_tests, asset


class Deck:
    def __init__(self, num_cards):
        self.cards = None
        self._temp = None
        self._num_cards = num_cards
        self.reset()
    
    def reset(self):
        self.cards = list(range(self._num_cards))
        self._temp = [0]*self._num_cards
    
    def deal_into_new_stack(self):
        self.cards.reverse()
    
    def cut(self, n):
        self._temp[:-n] = self.cards[n:]
        self._temp[-n:] = self.cards[:n]
        self.cards, self._temp = self._temp, self.cards
    
    def deal_with_increment(self, n):
        for i, card in enumerate(self.cards):
            self._temp[(i*n)%self._num_cards] = card
        
        self.cards, self._temp = self._temp, self.cards
    
    def shuffle(self, lines):
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



def _main():
    with open(asset("day22.txt")) as file:
        lines = list(file)
    
    deck = Deck(10007)
    deck.shuffle(file)
    print("Part 1:", deck.cards.index(2019))
    
    


if __name__ == "__main__":
    _main()
