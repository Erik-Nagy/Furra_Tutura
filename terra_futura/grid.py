from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from typing import Optional, List
from terra_futura.simple_types import *
import json

class Grid(InterfaceGrid):
    _cards: list[list[Optional[InterfaceCard]]] # storing cards in a 2d list
    _cardActivations: list[list[bool]] # storing cards in a 2d list
    _startingCardPosition: GridPosition
    
    def __init__(self) -> None:
        self._cards = [[None] * 3 for _ in range(3)]
        self._cardActivations = [[False] * 3 for _ in range(3)]
        self._startingCardPosition = GridPosition(1, 1)

    def _modifiedCoordinate(self, coordinate: GridPosition) -> GridPosition:
        # turns relative coordinates into absolute coordinates
        return GridPosition(self._startingCardPosition.x + coordinate.x,
                            self._startingCardPosition.y + coordinate.y)
    
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        absoluteCoordinate = self._modifiedCoordinate(coordinate)
        searchedPosition: Optional[InterfaceCard] = self._cards[absoluteCoordinate.y][absoluteCoordinate.x]
        return searchedPosition

    def canPutCard(self, coordinate: GridPosition) -> bool:
        absoluteCoordinate = self._modifiedCoordinate(coordinate)
        # check if position is empty
        return self._cards[absoluteCoordinate.y][absoluteCoordinate.x] is None

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> bool:
        absoluteCoordinate = self._modifiedCoordinate(coordinate)
        if self.canPutCard(absoluteCoordinate):
            self._cards[absoluteCoordinate.y][absoluteCoordinate.x] = card
            return True
        return False

    def canBeActivated(self, coordinate: GridPosition) -> bool:
        absoluteCoordinate = self._modifiedCoordinate(coordinate)
        if self.getCard(absoluteCoordinate) is None:
            return False
        return not self._cardActivations[absoluteCoordinate.y][absoluteCoordinate.x]
        
    def setActivated(self, coordinate: GridPosition) -> None:
        absoluteCoordinate = self._modifiedCoordinate(coordinate)
        self._cardActivations[absoluteCoordinate.y][absoluteCoordinate.x] = True

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        for pos in pattern:
            self.setActivated(pos)
        
    def endTurn(self) -> None:
        self._cardActivations = [[False] * 3 for _ in range(3)]

    def state(self) -> str:
        cards_state: list[dict[str, str]] = []
        for row in range(3):
            for col in range(3):
                card = self._cards[row][col]
                if card is not None:
                    cards_state.append({
                        "position": f"({row},{col})",
                        "card": card.state()
                    })
        return json.dumps({"cards": cards_state})