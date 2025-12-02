import random

from terra_futura.pile import Pile
from terra_futura.card import Card


def _make_cards(n: int):
    return [Card() for _ in range(n)]


def test_initial_state_counts():
    # test initial counts of hidden, visible and discarded cards
    random.seed(0)
    cards = _make_cards(7)
    p = Pile(cards)

    s = p.state()
    assert "- hidden cards: 3" in s
    assert "- visible cards: 4" in s
    assert "- discarded cards: 0" in s


def _visible_list(pile: Pile):
    # return list of visible cards
    out = []
    for i in range(1, 5):
        c = pile.getCard(i)
        if c is None:
            break
        out.append(c)
    return out


def test_takeCard():
    # test that taking a card removes it from visible cards
    random.seed(1)
    cards = _make_cards(6)
    p = Pile(cards)

    before = _visible_list(p)
    assert len(before) == 4

    removed = before[1]
    p.takeCard(2)

    after = _visible_list(p)
    assert removed not in after
    assert len(after) == 4


def test_removeLastCard():
    # test that removing last card works correctly
    random.seed(2)
    cards = _make_cards(6)
    p = Pile(cards)

    before = _visible_list(p)
    assert len(before) == 4

    p.removeLastCard()

    after = _visible_list(p)
    assert len(after) == 4
