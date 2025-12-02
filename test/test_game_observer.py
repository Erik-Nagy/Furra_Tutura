# test/test_game_observer.py

from typing import Dict
from unittest.mock import Mock

import pytest

from terra_futura.game_observer import GameObserver
from terra_futura.interfaces import TerraFuturaObserverInterface


def _make_observer() -> Mock:
    # Create a mock that behaves like TerraFuturaObserverInterface
    return Mock(spec=TerraFuturaObserverInterface)


def test_notify_all_forwards_state_to_correct_observers() -> None:
    observer1 = _make_observer()
    observer2 = _make_observer()
    observers: Dict[int, TerraFuturaObserverInterface] = {
        1: observer1,
        2: observer2,
    }

    game_observer = GameObserver(observers)

    new_state = {
        1: "state-for-player-1",
        2: "state-for-player-2",
    }

    game_observer.notifyAll(new_state)

    observer1.notify.assert_called_once_with("state-for-player-1")
    observer2.notify.assert_called_once_with("state-for-player-2")


def test_notify_all_ignores_unknown_player_ids() -> None:
    observer1 = _make_observer()
    observers: Dict[int, TerraFuturaObserverInterface] = {1: observer1}

    game_observer = GameObserver(observers)

    new_state = {
        1: "known-player-state",
        99: "unknown-player-state",  # no observer
    }

    game_observer.notifyAll(new_state)

    observer1.notify.assert_called_once_with("known-player-state")
    # Nothing to assert for player 99; the main check is “no exception”


def test_notify_all_with_empty_state_notifies_nobody() -> None:
    observer1 = _make_observer()
    observer2 = _make_observer()
    observers: Dict[int, TerraFuturaObserverInterface] = {
        1: observer1,
        2: observer2,
    }

    game_observer = GameObserver(observers)

    game_observer.notifyAll({})

    observer1.notify.assert_not_called()
    observer2.notify.assert_not_called()


def test_observers_property_returns_copy() -> None:
    observer1 = _make_observer()
    observers: Dict[int, TerraFuturaObserverInterface] = {1: observer1}

    game_observer = GameObserver(observers)

    external = game_observer.observers
    assert external == observers

    # Mutate the returned dict
    external[2] = _make_observer()

    # Internal mapping must not be affected
    # (accessing _observers is OK in a test)
    assert 2 not in game_observer._observers
    assert game_observer.observers.keys() == {1}
