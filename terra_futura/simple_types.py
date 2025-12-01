from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass

class GridPosition:
    _x: int
    _y: int

    def __init__(self, x: int, y: int):
        if x < -2 or x > 2 or y < -2 or y > 2:
            raise ValueError
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __str__(self) -> str:
        return f"({self._x},{self._y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GridPosition):
            return False
        return self._x == other._x and self._y == other._y

    def __hash__(self) -> int:
        return hash((self._x, self._y))


class Resource(Enum):
    YELLOW = auto()  # Raw material
    RED = auto()     # Raw material
    GREEN = auto()   # Raw material
    GOODS = auto()   # Product
    FOOD = auto()    # Product
    CONSTRUCTION = auto()  # Product
    MONEY = auto()
    POLLUTION = auto()  # Not a resource, but tracked


class Deck(Enum):
    LEVEL_I = auto()
    LEVEL_II = auto()


@dataclass(frozen=True)
class CardSource:
    deck: Deck
    index: int
    
    

@dataclass(frozen=True)
class Points:
    value: int
    
class GameState(Enum):
    TakeCardNoCardDiscarded = auto()
    TakeCardCardDiscarded = auto()
    ActivateCard = auto()
    SelectReward = auto()
    SelectActivationPattern = auto()
    SelectScoringMethod = auto()
    Finish = auto()