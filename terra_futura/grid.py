from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from typing import Optional, List, Set
from terra_futura.simple_types import *

class Grid (InterfaceGrid):
    def __init__(self) ->None:
        self._positions : dict[GridPosition, InterfaceCard] = {}
        self._activationPattern: List[GridPosition] = []
        self._activatedThisTurn: Set[GridPosition] = set()
    
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        return self._positions.get(coordinate)

    def canPutCard(self, coordinate: GridPosition)-> bool:
        if not self._positions:
            return True
        if coordinate in self._positions:
            return False
        
        allWidths = [pos.x for pos in self._positions.keys()] + [coordinate.x]
        allHeights = [pos.y for pos in self._positions.keys()] + [coordinate.y]
        newGridWidth = max(allWidths) - min(allWidths) + 1
        newGridHeight = max(allHeights) - min(allHeights) + 1

        if newGridWidth > 3 or newGridHeight >3:
            return False
        return True
        

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        if not self.canPutCard(coordinate):
            raise ValueError("Cannot put card on this position")
        
        if not self._positions and coordinate != GridPosition(0,0):
            raise ValueError("First card must be placed at (0,0)")
    
        self._positions[coordinate] = card

        pattern = [GridPosition(coordinate.x, y) for y in range(-2,3)] + [GridPosition(x, coordinate.y) for x in range(-2,3)]
        self.setActivationPattern(pattern)

    def canBeActivated(self, coordinate: GridPosition)-> bool:
        if (coordinate in self._positions and
            coordinate in self._activationPattern and
            coordinate not in self._activatedThisTurn):
            return True 
        return False
    
    def setActivated(self, coordinate: GridPosition) -> None:
        if not self.canBeActivated(coordinate):
            raise ValueError("Cannot activate this position")
        self._activatedThisTurn.add(coordinate)

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        self._activationPattern = pattern
        
    def endTurn(self) -> None:
        self._activatedThisTurn.clear()

    def state(self) -> str:
        positions_sorted = sorted(self._positions.items(), key=lambda item: (item[0].x, item[0].y))
        pos_strs = [f"({pos.x},{pos.y})" for pos, _ in positions_sorted]

        pattern_sorted = sorted(self._activationPattern, key=lambda p: (p.x, p.y))
        pattern_strs = [f"({p.x},{p.y})" for p in pattern_sorted]

        activated_sorted = sorted(self._activatedThisTurn, key=lambda p: (p.x, p.y))
        activated_strs = [f"({p.x},{p.y})" for p in activated_sorted]

        return (
            "Used positions: " + ", ".join(pos_strs)
            + "\nActivation pattern: " + ", ".join(pattern_strs)
            + "\nActivated this turn: " + ", ".join(activated_strs)
        )