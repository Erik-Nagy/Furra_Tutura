from __future__ import annotations
import unittest
from abc import abstractmethod

from typing import List, Optional
from terra_futura.simple_types import GridPosition, Resource
from terra_futura.interfaces import InterfaceGrid, InterfaceCard, InterfacePile, Effect
from terra_futura.move_card import MoveCard


class CardFake(InterfaceCard):
    def __init__(self) ->None:
        # Attributes
        self.resources: List[Resource] = []
        self.pollutionSpacesL: int = 0

        # Multiplicity 0..1 — may be None or an Effect instance
        self.upperEffect: Optional[Effect] = None
        self.lowerEffect: Optional[Effect] = None

    # --- Interface methods ---
#not used
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
        return False

    def placePollution(self, amount: int = 1) -> None:
        pass


    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return True

    def checkLower(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return True

    def hasAssistance(self) -> bool:
        return True

    def state(self) -> str:
        return ""

class GridFake(InterfaceGrid):
#used
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        ...

#used
    def canPutCard(self, coordinate: GridPosition)-> bool:
        return True

 #used
    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> bool:
        return True

# not used
    def canBeActivated(self, coordinate: GridPosition)-> bool:
        return False
        
    def setActivated(self, coordinate: GridPosition) -> None:
        ...

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        ...
        
    def endTurn(self) -> None:
        ...

    def state(self) -> str:
        return ""

class GridCannotPutCardFake(InterfaceGrid):
#used
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        ...

#used
    def canPutCard(self, coordinate: GridPosition)-> bool:
        return True

 #used
    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> bool:
        return False

# not used
    def canBeActivated(self, coordinate: GridPosition)-> bool:
        return False
        
    def setActivated(self, coordinate: GridPosition) -> None:
        ...

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        ...
        
    def endTurn(self) -> None:
        ...

    def state(self) -> str:
        return ""

class PileFake(InterfacePile):
    """Only gives the card information, does not change anything"""
    def getCard(self, index:int) ->Optional[InterfaceCard]:
        card = CardFake()

        return card

    """Removes card from grid."""
    def takeCard(self, index: int) -> None:
        ...

    def removeLastCard(self) -> None:
        ...

    def state(self)-> str:
        return ""

class PileUnableToGiveCardFake(InterfacePile):
    def getCard(self, index:int) ->Optional[InterfaceCard]:
        return None

    def takeCard(self, index: int) -> None:
        ...

    def removeLastCard(self) -> None:
        ...

    def state(self)-> str:
        return ""


class TestMoveCard(unittest.TestCase):
    def setUp(self) ->None:
        
        self.move_card = MoveCard()

        self.pile = PileFake()
        self.notGeneratingPile = PileUnableToGiveCardFake()

        self.grid = GridFake()
        self.notPuttingGrid = GridCannotPutCardFake()



    def test_move_card_correct(self) ->None:
        self.assertEqual(True,  self.move_card.moveCard(self.pile,0,GridPosition(0,0),self.grid))

    def test_move_card_correct2(self) ->None:
        self.assertEqual(True,  self.move_card.moveCard(self.pile,0,GridPosition(2,1),self.grid))

    def test_move_card_wrong_position(self) ->None:
        with self.assertRaises(ValueError):
            self.move_card.moveCard(self.pile,0,GridPosition(67,0),self.grid)

    def test_cannot_get_card_card(self) ->None:
        self.assertEqual(False,  self.move_card.moveCard(self.notGeneratingPile,0,GridPosition(0,0),self.grid))

    def test_grid_cannot_put_card(self) ->None:
        with self.assertRaises(AssertionError):
            self.move_card.moveCard(self.pile, 0, GridPosition(0,0), self.notPuttingGrid)
