import pytest
from typing import List
from terra_futura.pile import Pile, InterfaceShuffler, RandomShuffler
from terra_futura.interfaces import InterfaceCard, Resource


class FakeCard(InterfaceCard):
    """Simple stand-in for InterfaceCard."""

    def __init__(self, name: str) -> None:
        self.name = name

    def state(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"FakeCard({self.name})"
    
    # --- Interface methods ---
    def isActive(self) -> bool:
        return True

    def canPutResources(self, resources: List[Resource]) -> bool:
        return True

    def putResources(self, resources: List[Resource]) -> None:
        pass

    def canGetResources(self, resources: List[Resource]) -> bool:
        return True

    def getResources(self, resources: List[Resource]) -> None:
        pass

    def canPlacePollution(self, amount: int = 1) -> bool:
        return True

    def placePollution(self, amount: int = 1) -> None:
        pass

    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return True

    def checkLower(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return True

    def hasAssistance(self) -> bool:
        return True


class FakeShuffler(InterfaceShuffler):
    def __init__(self) -> None:
        self.calls: list[list[InterfaceCard]] = []

    def shuffle(self, deck: list[InterfaceCard]) -> list[InterfaceCard]:
        self.calls.append(list(deck))
        return list(deck)


def _make_cards(*names: str) -> list[FakeCard]:
    return [FakeCard(n) for n in names]


def test_init_requires_exactly_four_visible_cards() -> None:
    """Test that constructor requires exactly 4 visible cards."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1", "h2")
    shuffler = FakeShuffler()
    
    # Should work with exactly 4 visible
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    assert len(pile.visible_cards) == 4
    
    # Should fail with less than 4
    with pytest.raises(ValueError, match="Not 4 visible cards"):
        Pile(visible_cards=_make_cards("v1", "v2", "v3"), 
             hidden_cards=hidden, 
             shuffler=shuffler)
    
    # Should fail with more than 4
    with pytest.raises(ValueError, match="Not 4 visible cards"):
        Pile(visible_cards=_make_cards("v1", "v2", "v3", "v4", "v5"), 
             hidden_cards=hidden, 
             shuffler=shuffler)


def test_getCard_returns_card_for_valid_index_and_none_out_of_range() -> None:
    """Test getCard returns correct card or None for invalid index."""
    visible = _make_cards("a", "b", "c", "d")
    hidden = _make_cards("x")
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=FakeShuffler())

    # valid indices (1-4)
    x = pile.getCard(1)
    assert x and x.state() == "a"
    
    y = pile.getCard(2)
    assert y and y.state() == "b"
    
    z = pile.getCard(3)
    assert z and z.state() == "c"
    
    w = pile.getCard(4)
    assert w and w.state() == "d"

    # out of range indices
    assert pile.getCard(0) is None
    assert pile.getCard(5) is None
    assert pile.getCard(6) is None


def test_takeCard_removes_selected_and_refills_from_hidden() -> None:
    """Test takeCard removes selected card and refills from hidden deck."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1", "h2")
    shuffler = FakeShuffler()
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)

    # Take card at position 2 (v2)
    taken = pile.takeCard(2)
    
    # Should return v2
    assert taken.state() == "v2"
    
    # Visible should still have 4 cards
    assert len(pile.visible_cards) == 4
    
    # h2 should be added to position 1 (beginning), v1 moved to position 2, etc.
    # After taking v2 at index 1 (0-based), we pop it and insert topDeck (h2) at beginning
    # So visible becomes: [h2, v1, v3, v4]
    assert [c.state() for c in pile.visible_cards] == ["h2", "v1", "v3", "v4"]
    
    # Hidden should now have only h1
    assert len(pile.hidden_cards) == 1
    assert pile.hidden_cards[0].state() == "h1"
    
    # No discards yet
    assert pile.discarded_cards == []


def test_takeCard_position_5_returns_top_card_from_hidden() -> None:
    """Test that takeCard(5) returns the top card from hidden deck."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1", "h2", "h3")
    shuffler = FakeShuffler()
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)

    # Position 5 should return top card from hidden (h3)
    taken = pile.takeCard(5)
    assert taken.state() == "h3"
    
    # Visible cards should remain unchanged
    assert [c.state() for c in pile.visible_cards] == ["v1", "v2", "v3", "v4"]
    
    # Hidden should now have h1, h2
    assert len(pile.hidden_cards) == 2
    assert [c.state() for c in pile.hidden_cards] == ["h1", "h2"]


def test_takeCard_reshuffles_discarded_when_hidden_empty() -> None:
    """Test that takeCard reshuffles discarded cards when hidden is empty."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = []  # Empty hidden deck
    discarded = _make_cards("d1", "d2", "d3")
    shuffler = FakeShuffler()
    
    # Create pile with empty hidden
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    # Manually set discarded cards
    pile.discarded_cards = discarded
    
    # Take a card - should trigger reshuffle
    taken = pile.takeCard(1)
    
    # Shuffler should have been called with discarded cards
    assert len(shuffler.calls) == 1
    assert [c.state() for c in shuffler.calls[0]] == ["d1", "d2", "d3"]
    
    # Discarded should be cleared
    assert pile.discarded_cards == []
    
    # Hidden should now contain shuffled discarded cards - the one we took to fill in the visible ones
    assert len(pile.hidden_cards) == 2

    assert len(pile.visible_cards) == 4


def test_takeCard_raises_error_when_no_cards_available() -> None:
    """Test takeCard raises ValueError when no cards are available."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = []  # Empty
    shuffler = FakeShuffler()
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    
    # No discarded cards either, so reshuffle will return empty list
    # Should raise ValueError
    with pytest.raises(ValueError, match="Empty pile"):
        pile.takeCard(1)


def test_removeLastCard_discards_oldest_and_refills_from_hidden() -> None:
    """Test removeLastCard discards last visible card and refills."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1", "h2")
    shuffler = FakeShuffler()
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)

    # Remove last card
    pile.removeLastCard()
    
    # v4 should be in discarded
    assert len(pile.discarded_cards) == 1
    assert pile.discarded_cards[0].state() == "v4"
    
    # Visible should have 4 cards: h2 at beginning, then v1, v2, v3
    assert len(pile.visible_cards) == 4
    assert [c.state() for c in pile.visible_cards] == ["h2", "v1", "v2", "v3"]
    
    # Hidden should have only h1
    assert len(pile.hidden_cards) == 1
    assert pile.hidden_cards[0].state() == "h1"


def test_removeLastCard_reshuffles_when_hidden_empty() -> None:
    """Test removeLastCard reshuffles discarded cards when hidden is empty."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = []  # Empty
    discarded = _make_cards("d1", "d2")
    shuffler = FakeShuffler()
    
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    pile.discarded_cards = discarded
    
    # Remove last card - should trigger reshuffle
    pile.removeLastCard()
    
    # Shuffler should have been called
    assert len(shuffler.calls) == 1
    assert [c.state() for c in shuffler.calls[0]] == ["d1", "d2"]
    
    # Discarded should now contain v4
    assert len(pile.discarded_cards) == 1
    assert pile.discarded_cards[0].state() == "v4"
    assert [c.state() for c in pile.visible_cards] == ["d2", "v1", "v2", "v3"]
    assert [c.state() for c in pile.hidden_cards] == ["d1"]


def test_removeLastCard_raises_error_when_no_cards_available() -> None:
    """Test removeLastCard raises ValueError when no cards are available."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = []  # Empty
    shuffler = FakeShuffler()
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    
    # No discarded cards either, so reshuffle will return empty list
    # Should raise ValueError
    with pytest.raises(ValueError, match="Empty pile"):
        pile.removeLastCard()


def test_state_returns_correct_format() -> None:
    """Test that state() returns the correct string format."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1", "h2")
    discarded = _make_cards("d1")
    
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=FakeShuffler())
    pile.discarded_cards = discarded
    
    state_str = pile.state()
    
    # Check format
    lines = state_str.strip().split('\n')
    assert len(lines) == 7  # 4 visible + 2 hidden + 1 discarded
    
    # Check visible lines
    assert "Visible 0: v1" in state_str
    assert "Visible 1: v2" in state_str
    assert "Visible 2: v3" in state_str
    assert "Visible 3: v4" in state_str



def test_default_shuffler_is_RandomShuffler() -> None:
    """Test that default shuffler is RandomShuffler."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1")
    
    # Create without specifying shuffler
    pile = Pile(visible_cards=visible, hidden_cards=hidden)
    
    # Should use RandomShuffler by default
    assert isinstance(pile.shuffler, RandomShuffler)


def test_shuffler_parameter_is_used_when_provided() -> None:
    """Test that custom shuffler is used when provided."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1")
    shuffler = FakeShuffler()
    
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=shuffler)
    
    assert pile.shuffler is shuffler


def test_takeCard_with_invalid_index_raises_error() -> None:
    """Test that takeCard raises ValueError for invalid indices."""
    visible = _make_cards("v1", "v2", "v3", "v4")
    hidden = _make_cards("h1")
    pile = Pile(visible_cards=visible, hidden_cards=hidden, shuffler=FakeShuffler())
    
    # Test invalid indices
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(0)
    
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(6)
    
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(-1)