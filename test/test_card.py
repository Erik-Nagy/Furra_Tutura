# test_card.py
from collections import Counter
from dataclasses import dataclass
from typing import List

import pytest

# Adjust these imports to your real module paths
from terra_futura.card import Card
from terra_futura.interfaces import Effect
from terra_futura.simple_types import Resource

# ---------------------------------------------------------------------------
# Dummy resource + dummy effects for testing
# ---------------------------------------------------------------------------



class AlwaysTrueEffect(Effect):
    """Effect that always accepts any (input, output, pollution)."""

    def __init__(self, assistance: bool = False, label: str = "true"):
        self._assistance = assistance
        self._label = label
        self.calls: int = 0  # track how many times check() is called

    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        self.calls += 1
        return True

    def hasAssistance(self) -> bool:
        return self._assistance

    def state(self) -> str:
        return self._label


class AlwaysFalseEffect(Effect):
    """Effect that always rejects."""

    def __init__(self, assistance: bool = False, label: str = "false"):
        self._assistance = assistance
        self._label = label
        self.calls: int = 0

    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        self.calls += 1
        return False

    def hasAssistance(self) -> bool:
        return self._assistance

    def state(self) -> str:
        return self._label


# ---------------------------------------------------------------------------
# Basic card & pollution behavior
# ---------------------------------------------------------------------------

def test_new_card_is_active_and_clean() -> None:
    c = Card(pollutionSpacesL=3)
    assert c.is_active is True
    assert c.pollution == 0


def test_placePollution_fills_slots_then_center_and_deactivates() -> None:
    c = Card(pollutionSpacesL=3)

    # First cube: goes to slots
    c.placePollution(1)
    assert c.pollution == 1
    assert c.is_active is True

    # Next 2 cubes:
    # - one fills last free slot
    # - one goes to center, card becomes inactive
    c.placePollution(2)
    assert c.pollution == 3
    assert c.is_active is False


def test_cannot_placePollution_on_inactive_card() -> None:
    c = Card(pollutionSpacesL=1)

    # First cube goes directly to center -> inactive
    c.placePollution(1)
    assert c.is_active is False

    with pytest.raises(ValueError):
        c.placePollution(1)  # cannot place on inactive card

def test_cannot_place_too_much_pollution() -> None:
    c = Card(pollutionSpacesL=5)

    # First cube goes directly to center -> inactive

    with pytest.raises(ValueError):
        c.placePollution(69)  # cannot place on inactive card


# ---------------------------------------------------------------------------
# Resource management
# ---------------------------------------------------------------------------

def test_get_resources_on_active_card() -> None:
    c = Card(pollutionSpacesL=1)
    
    r1 = Resource.GREEN
    r2 = Resource.RED

    assert c.canPutResources([r1, r2]) is True
    c.putResources([r1, r2])
    assert Counter(c.resources) == Counter([r1, r2])


def test_get_resources_on_inactive_card_fails() -> None:
    c = Card(pollutionSpacesL=1)
    c.placePollution(1)  

    r = Resource.GREEN
    assert c.canPutResources([r]) is False
    with pytest.raises(ValueError):
        c.putResources([r])


def test_can_put_resources_checks_multiset_and_activity() -> None:
    c = Card(pollutionSpacesL=1)
    r1 = Resource.GREEN
    r2 = Resource.RED

    c.putResources([r1, r1, r2]) 

    assert c.canGetResources([r1, r2]) is True
    assert c.canGetResources([r1, r1, r1]) is False

    c.placePollution(1)
    assert c.is_active is False
    assert c.canGetResources([r1]) is False


def test_put_resources_removes_exact_multiset() -> None:
    c = Card(pollutionSpacesL=1)
    w = Resource.GREEN
    b = Resource.RED
    s = Resource.GOODS

    c.putResources([w, w, b, s])

    c.getResources([w, b]) 

    assert Counter(c.resources) == Counter([w, s])

    with pytest.raises(ValueError):
        c.getResources([b])


# ---------------------------------------------------------------------------
# check / checkLower integration with effects
# ---------------------------------------------------------------------------

def test_check_uses_upper_effect_when_card_is_active_and_preconditions_ok() -> None:
    w = Resource.GREEN
    reward = Resource.FOOD

    eff = AlwaysTrueEffect()
    c = Card(pollutionSpacesL=2, upperEffect=eff)

    # Prepare card so it can pay input
    c.putResources([w])

    result = c.check(input=[w], output=[reward], pollution=1)

    assert result is True
    assert eff.calls == 1  # Effect.check was invoked
    # Pollution was only validated, not placed here (Card.check is just validation)


def test_check_returns_false_if_no_upper_effect() -> None:
    c = Card(pollutionSpacesL=2, upperEffect=None)
    w = Resource.GREEN
    reward = Resource.FOOD

    c.putResources([w])
    assert c.check(input=[w], output=[reward], pollution=0) is False


def test_check_does_not_call_effect_if_card_inactive() -> None:
    w = Resource.GREEN
    reward = Resource.FOOD

    eff = AlwaysTrueEffect()
    c = Card(pollutionSpacesL=1, upperEffect=eff)
    c.putResources([w])

    # make card inactive
    c.placePollution(1)
    assert c.is_active is False

    result = c.check(input=[w], output=[reward], pollution=0)
    assert result is False
    assert eff.calls == 0  # effect not called when preconditions fail


def test_check_fails_if_card_cannot_pay_input() -> None:
    w = Resource.GREEN
    reward = Resource.FOOD

    eff = AlwaysTrueEffect()
    c = Card(pollutionSpacesL=2, upperEffect=eff)

    # Card has no resources, so cannot pay wood
    assert c.canGetResources([w]) is False
    result = c.check(input=[w], output=[reward], pollution=0)
    assert result is False
    assert eff.calls == 0


def test_check_lower_uses_lower_effect_similarly() -> None:
    w = Resource.GREEN
    reward = Resource.FOOD

    eff_upper = AlwaysFalseEffect(label="upper")
    eff_lower = AlwaysTrueEffect(label="lower")
    c = Card(pollutionSpacesL=1, upperEffect=eff_upper, lowerEffect=eff_lower)

    c.putResources([w])
    result_upper = c.check(input=[w], output=[reward], pollution=0)
    result_lower = c.checkLower(input=[w], output=[reward], pollution=0)

    assert result_upper is False  # upper effect always false
    assert result_lower is True   # lower effect always true
    assert eff_lower.calls == 1


# ---------------------------------------------------------------------------
# hasAssistance and state()
# ---------------------------------------------------------------------------

def test_has_assistance_true_if_upper_or_lower_has_assistance() -> None:
    upper = AlwaysTrueEffect(assistance=True)
    lower = AlwaysFalseEffect(assistance=False)
    c1 = Card(pollutionSpacesL=1, upperEffect=upper, lowerEffect=lower)

    assert c1.hasAssistance() is True

    upper2 = AlwaysFalseEffect(assistance=False)
    lower2 = AlwaysTrueEffect(assistance=True)
    c2 = Card(pollutionSpacesL=1, upperEffect=upper2, lowerEffect=lower2)

    assert c2.hasAssistance() is True

    upper3 = AlwaysFalseEffect(assistance=False)
    lower3 = AlwaysFalseEffect(assistance=False)
    c3 = Card(pollutionSpacesL=1, upperEffect=upper3, lowerEffect=lower3)

    assert c3.hasAssistance() is False


def test_state_contains_basic_info() -> None:
    c = Card(pollutionSpacesL=3)
    w = Resource.GREEN

    c.putResources([w])
    c.placePollution(1)

    s = c.state()

    assert "active" in s    # still active, only on slot
    assert "resources=1" in s
    assert "pollution=1/3" in s

    # now deactivate
    c.placePollution(2)
    s2 = c.state()
    assert "inactive" in s2

def test_has_this_effect() -> None:
    upper = AlwaysTrueEffect(assistance=True)
    c1 = Card(pollutionSpacesL=1, upperEffect=upper)

    assert "true" in c1.state()
    assert "false" not in c1.state()
    assert "No effect" in c1.state()

    lower = AlwaysFalseEffect(assistance=False)
    c2 = Card(pollutionSpacesL=1, lowerEffect=lower)

    assert "true" not in c2.state()
    assert "false" in c2.state()
    assert "No effect" in c2.state()

    upper = AlwaysTrueEffect(assistance=True)
    lower = AlwaysFalseEffect(assistance=False)
    c3 = Card(pollutionSpacesL=1, upperEffect=upper, lowerEffect=lower)

    assert "true" in c3.state()
    assert "false" in c3.state()

    c4 = Card(pollutionSpacesL=1)

    assert "true" not in c4.state()
    assert "false" not in c4.state()
    assert "No effect" in c4.state()