import pytest

from terra_futura.game_observer import GameObserver
from terra_futura.interfaces import TerraFuturaObserverInterface
from typing import List


class DummyObserver(TerraFuturaObserverInterface):
    """
    Simple test double that collects all states passed to notify().
    """

    def __init__(self) -> None:
        self.received_states: List[str] = []

    def notify(self, game_state: str) -> None:
        self.received_states.append(game_state)


def test_single_observer_receives_notifications() -> None:
    dispatcher = GameObserver()
    observer = DummyObserver()

    dispatcher.register_observer(1, observer)
    dispatcher.notify("STATE_A")

    assert observer.received_states == ["STATE_A"]


def test_multiple_observers_receive_broadcast() -> None:
    dispatcher = GameObserver()
    obs1 = DummyObserver()
    obs2 = DummyObserver()

    dispatcher.register_observer(1, obs1)
    dispatcher.register_observer(2, obs2)

    dispatcher.notify("TURN_START")

    assert obs1.received_states == ["TURN_START"]
    assert obs2.received_states == ["TURN_START"]


def test_unregister_observer_stops_notifications() -> None:
    dispatcher = GameObserver()
    obs1 = DummyObserver()
    obs2 = DummyObserver()

    dispatcher.register_observer(1, obs1)
    dispatcher.register_observer(2, obs2)

    dispatcher.notify("BEFORE_REMOVE")

    dispatcher.unregister_observer(1)

    dispatcher.notify("AFTER_REMOVE")

    # obs1 only receives the first state
    assert obs1.received_states == ["BEFORE_REMOVE"]
    # obs2 receives both
    assert obs2.received_states == ["BEFORE_REMOVE", "AFTER_REMOVE"]


def test_notify_with_no_observers_does_not_fail() -> None:
    dispatcher = GameObserver()

    # Should not raise
    dispatcher.notify("ANY_STATE")