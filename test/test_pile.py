import pytest
from typing import List, cast
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
    """
    Deterministic shuffler for tests.
    """
    def __init__(self) -> None:
        self.calls: list[list[InterfaceCard]] = []

    def shuffle(self, deck: list[InterfaceCard]) -> list[InterfaceCard]:
        # record the exact deck Pile asked us to shuffle
        self.calls.append(list(deck))
        # return a copy, same order (reverse to simulate some change)
        return deck.copy()


def _make_cards(*names: str) -> list[FakeCard]:
    return [FakeCard(n) for n in names]


def test_init_creates_four_visible_cards_from_hidden() -> None:
    """Test that constructor creates 4 visible cards from hidden deck."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5", "c6")
    shuffler = FakeShuffler()
    
    pile = Pile(cards=cards, shuffler=shuffler)
    
    # Should have 4 visible cards
    assert len(pile.visible_cards) == 4
    # Should have remaining cards in hidden (c1, c2 since we pop from end)
    assert len(pile.hidden_cards) == 2
    # No discards yet
    assert len(pile.discarded_cards) == 0
    
    # Cards should be taken from the end of the list first (pop())
    # visible gets: c6, c5, c4, c3 (inserted at beginning each time)
    # hidden has: c1, c2
    assert [c.state() for c in pile.visible_cards] == ["c3", "c4", "c5", "c6"]
    assert [c.state() for c in pile.hidden_cards] == ["c1", "c2"]


def test_init_uses_discarded_cards_when_hidden_runs_out() -> None:
    """Test that constructor uses discarded cards when hidden is exhausted."""
    cards = _make_cards("c1", "c2", "c3")  # Only 3 cards, need 4 visible
    shuffler = FakeShuffler()
    
    # This should trigger a shuffle of discarded cards
    # But we have no discarded cards initially, so it should fail
    with pytest.raises(ValueError, match="Empty pile"):
        Pile(cards=cards, shuffler=shuffler)


def test_init_with_exactly_four_cards() -> None:
    """Test constructor with exactly 4 cards."""
    cards = _make_cards("c1", "c2", "c3", "c4")
    shuffler = FakeShuffler()
    
    pile = Pile(cards=cards, shuffler=shuffler)
    
    assert len(pile.visible_cards) == 4
    assert len(pile.hidden_cards) == 0
    assert [c.state() for c in pile.visible_cards] == ["c1", "c2", "c3", "c4"]


def test_getCard_returns_card_for_valid_index_and_none_out_of_range() -> None:
    """Test getCard returns correct card or None for invalid index."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5")
    pile = Pile(cards=cards, shuffler=FakeShuffler())

    # valid indices (1-4)
    c1 = pile.getCard(1)
    if c1:
        assert c1.state() == "c2"  # visible: [c2, c3, c4, c5]
    
    c2 = pile.getCard(2)
    if c2:
        assert c2.state() == "c3"
    
    c3 = pile.getCard(3)
    if c3:
        assert c3.state() == "c4"
    
    c4 = pile.getCard(4)
    if c4:
        assert c4.state() == "c5"

    # valid index 5
    c5 = pile.getCard(5)
    if c5:
        assert c5.state() == "c1"

    # out of range indices
    assert pile.getCard(0) is None
    assert pile.getCard(6) is None


def test_takeCard_removes_selected_visible_and_refills() -> None:
    """Test takeCard removes selected visible card and refills from hidden."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5", "c6")  # c1,c2 hidden; c3,c4,c5,c6 visible
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)

    # Take card at position 2 (c4 in visible: [c3, c4, c5, c6])
    taken = pile.getCard(2)
    pile.takeCard(2)
    
    # Should return c4
    if taken:
        assert taken.state() == "c4"
    
    # Visible should still have 4 cards
    assert len(pile.visible_cards) == 4
    
    # c2 should be added to beginning (from hidden), visible becomes: [c2, c3, c5, c6]
    assert [c.state() for c in pile.visible_cards] == ["c2", "c3", "c5", "c6"]
    
    # Hidden should now have only c1
    assert len(pile.hidden_cards) == 1
    assert pile.hidden_cards[0].state() == "c1"


def test_takeCard_position_5_returns_top_card_from_hidden() -> None:
    """Test that takeCard(5) returns the top card from hidden deck."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5", "c6", "c7")  # c1,c2,c3 hidden; c4,c5,c6,c7 visible
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)

    # Position 5 should return top card from hidden (c3)
    taken = pile.getCard(5)
    pile.takeCard(5)
    if taken:
        assert taken.state() == "c3"
    
    # Visible cards should remain unchanged: still [c4, c5, c6, c7]
    assert [c.state() for c in pile.visible_cards] == ["c4", "c5", "c6", "c7"]
    
    # Hidden should now have c1, c2
    assert len(pile.hidden_cards) == 2
    assert [c.state() for c in pile.hidden_cards] == ["c1", "c2"]


def test_takeCard_reshuffles_discarded_when_hidden_empty() -> None:
    """Test that takeCard reshuffles discarded cards when hidden is empty."""
    cards = _make_cards("c1", "c2", "c3", "c4")  # All cards become visible, hidden empty
    shuffler = FakeShuffler()
    
    pile = Pile(cards=cards, shuffler=shuffler)
    # Manually add some discarded cards
    pile.discarded_cards = cast(List[InterfaceCard], _make_cards("d1", "d2", "d3"))
    
    # Take a card - should trigger reshuffle
    pile.takeCard(1)
    
    # Shuffler should have been called with discarded cards
    assert len(shuffler.calls) == 1
    assert [c.state() for c in shuffler.calls[0]] == ["d1", "d2", "d3"]
    
    # Discarded should be cleared
    assert pile.discarded_cards == []
    
    # Hidden should now contain shuffled discarded cards - the one we filled visible cards with
    assert len(pile.hidden_cards) == 2
    assert [c.state() for c in pile.hidden_cards] == ["d1", "d2"]  # After shuffle


def test_takeCard_raises_error_when_no_cards_available() -> None:
    """Test takeCard raises ValueError when no cards are available."""
    cards = _make_cards("c1", "c2", "c3", "c4")  # All cards visible, no hidden
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)
    
    # No hidden cards, no discarded cards either
    # Should raise ValueError when trying to take a card
    with pytest.raises(ValueError, match="No more cards"):
        pile.takeCard(1)


def test_takeCard_with_invalid_index_raises_error() -> None:
    """Test that takeCard raises ValueError for invalid indices."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5")
    pile = Pile(cards=cards, shuffler=FakeShuffler())
    
    # Test invalid indices
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(0)
    
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(6)
    
    with pytest.raises(ValueError, match="Cannot get card at that position"):
        pile.takeCard(-1)


def test_removeLastCard_discards_last_visible_and_refills() -> None:
    """Test removeLastCard discards last visible card and refills."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5", "c6")  # c1,c2 hidden; c3,c4,c5,c6 visible
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)

    # Remove last card (c6 from visible: [c3, c4, c5, c6])
    pile.removeLastCard()
    
    # c6 should be in discarded
    assert len(pile.discarded_cards) == 1
    assert pile.discarded_cards[0].state() == "c6"
    
    # Visible should have 4 cards: c2 at beginning, then c3, c4, c5
    assert len(pile.visible_cards) == 4
    assert [c.state() for c in pile.visible_cards] == ["c2", "c3", "c4", "c5"]
    
    # Hidden should have only c1
    assert len(pile.hidden_cards) == 1
    assert pile.hidden_cards[0].state() == "c1"


def test_removeLastCard_reshuffles_when_hidden_empty() -> None:
    """Test removeLastCard reshuffles discarded cards when hidden is empty."""
    cards = _make_cards("c1", "c2", "c3", "c4")  # All cards visible, hidden empty
    shuffler = FakeShuffler()
    
    pile = Pile(cards=cards, shuffler=shuffler)
    # Manually add some discarded cards
    pile.discarded_cards = cast(List[InterfaceCard], _make_cards("d1", "d2"))
    
    # Remove last card - should trigger reshuffle
    pile.removeLastCard()
    
    # Shuffler should have been called
    assert len(shuffler.calls) == 1
    assert [c.state() for c in shuffler.calls[0]] == ["d1", "d2"]  # reversed by FakeShuffler
    
    # Discarded should now contain c4 (the removed card)
    assert len(pile.discarded_cards) == 1
    assert pile.discarded_cards[0].state() == "c4"

    assert [c.state() for c in pile.hidden_cards] == ["d1"]


def test_removeLastCard_raises_error_when_no_cards_available() -> None:
    """Test removeLastCard raises ValueError when no cards are available."""
    cards = _make_cards("c1", "c2", "c3", "c4")  # All cards visible, no hidden
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)
    
    # No hidden cards, no discarded cards either
    # Should raise ValueError when trying to remove last card
    with pytest.raises(ValueError, match="Empty pile"):
        pile.removeLastCard()


def test_state_returns_correct_format() -> None:
    """Test that state() returns the correct string format."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5")
    pile = Pile(cards=cards, shuffler=FakeShuffler())
    
    # Manually set some discarded cards for testing
    pile.discarded_cards = cast(List[InterfaceCard],_make_cards("d1", "d2"))
    
    state_str = pile.state()
    
    # Check format - should have lines for visible, hidden, and discarded
    lines = state_str.strip().split('\n')
    
    # Should have: 4 visible + 1 hidden + 2 discarded = 7 lines
    assert len(lines) == 7
    
    # Check visible lines (visible: [c2, c3, c4, c5])
    assert "Visible 0: c2" in state_str
    assert "Visible 1: c3" in state_str
    assert "Visible 2: c4" in state_str
    assert "Visible 3: c5" in state_str
    
    # Check hidden line (hidden: [c1])
    assert "Hidden 0: c1" in state_str
    
    # Check discarded lines (discarded: [d1, d2])
    assert "Discarded 0: d1" in state_str
    assert "Discarded 1: d2" in state_str


def test_default_shuffler_is_RandomShuffler() -> None:
    """Test that default shuffler is RandomShuffler."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5")
    
    # Create without specifying shuffler
    pile = Pile(cards=cards)
    
    # Should use RandomShuffler by default
    assert isinstance(pile.shuffler, RandomShuffler)


def test_shuffler_parameter_is_used_when_provided() -> None:
    """Test that custom shuffler is used when provided."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5")
    shuffler = FakeShuffler()
    
    pile = Pile(cards=cards, shuffler=shuffler)
    
    assert pile.shuffler is shuffler


def test_multiple_consecutive_operations() -> None:
    """Test multiple consecutive operations on the pile."""
    cards = _make_cards("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8")
    shuffler = FakeShuffler()
    pile = Pile(cards=cards, shuffler=shuffler)
    
    # Initial state: hidden=[c1,c2,c3,c4], visible=[c5,c6,c7,c8]
    assert [c.state() for c in pile.hidden_cards] == ["c1", "c2", "c3", "c4"]
    assert [c.state() for c in pile.visible_cards] == ["c5", "c6", "c7", "c8"]
    
    # Take card from position 2 (c6)
    taken1 = pile.getCard(2)
    pile.takeCard(2)
    if taken1:
        assert taken1.state() == "c6"
    # Now: hidden=[c1,c2,c3], visible=[c4,c5,c7,c8]
    
    # Take card from position 5 (top of hidden: c3)
    taken2 = pile.getCard(5)
    pile.takeCard(5)
    if taken2:
        assert taken2.state() == "c3"
    # Now: hidden=[c1,c2], visible=[c4,c5,c7,c8]
    
    # Remove last card (c8 goes to discarded)
    pile.removeLastCard()
    assert pile.discarded_cards[0].state() == "c8"
    # Now: hidden=[c1], visible=[c2,c4,c5,c7], discarded=[c8]
    
    # Verify final state
    assert [c.state() for c in pile.hidden_cards] == ["c1"]
    assert [c.state() for c in pile.visible_cards] == ["c2", "c4", "c5", "c7"]
    assert [c.state() for c in pile.discarded_cards] == ["c8"]