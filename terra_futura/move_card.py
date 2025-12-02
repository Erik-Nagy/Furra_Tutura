from __future__ import annotations
import json
from typing import List, Tuple, Any
from terra_futura.simple_types import GridPosition
from terra_futura.interfaces import InterfaceMoveCard, InterfaceGrid, InterfacePile

class MoveCard(InterfaceMoveCard):
    def __init__(self) -> None:
        pass

    def moveCard(self, pile: InterfacePile,cardIndex: int, gridCoordinate: GridPosition, grid: InterfaceGrid) ->bool:
        # implementacia 

        if not grid.canPutCard(gridCoordinate):
            return False

        # Get the card from grid
        card = pile.getCard(cardIndex)

        # Check if there's a card
        if card is None:
            return False
        
        # Remove card from grid
        pile.takeCard(cardIndex)


        grid.putCard(gridCoordinate, card)

        return True