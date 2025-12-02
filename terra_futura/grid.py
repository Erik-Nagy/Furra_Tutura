from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from typing import Optional, List, Set
from terra_futura.simple_types import *

class Grid (InterfaceGrid):
    def __init__(self) ->None:
        self._positions : dict[GridPosition, InterfaceCard] = {}
        self._activationPattern: List[GridPosition] = []
        self._activatedThisTurn: Set[GridPosition] = set()
        self._canBeActivatedThisTurn: Set[GridPosition] = set()
        self._endPhase : bool = False
    
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        return self._positions.get(coordinate)

    def canPutCard(self, coordinate: GridPosition)-> bool:
        if not self._positions:
            return True
        if coordinate in self._positions:
            return False
        if self._canBeActivatedThisTurn or self._endPhase:
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

        for y in range(-2,3):
            self._canBeActivatedThisTurn.add(GridPosition(coordinate.x, y))
        for x in range(-2,3):
            self._canBeActivatedThisTurn.add(GridPosition(x, coordinate.y))

    def canBeActivated(self, coordinate: GridPosition)-> bool:
        if coordinate in self._positions and coordinate in self._activationPattern:
            return True
        if (coordinate in self._positions and
            coordinate in self._canBeActivatedThisTurn  and
            coordinate not in self._activatedThisTurn):
            return True 
        return False
    
    def setActivated(self, coordinate: GridPosition) -> None:
        if not self.canBeActivated(coordinate):
            raise ValueError("Cannot activate this position")
        self._activatedThisTurn.add(coordinate)
        if self._activationPattern:
            self._activationPattern.remove(coordinate)

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        if not pattern:
            self._activationPattern = []
            return

        if not self._positions:
            origin = GridPosition(0, 0)
        else:
            xs = [p.x for p in self._positions.keys()]
            ys = [p.y for p in self._positions.keys()]
            min_x = min(xs)
            min_y = min(ys)

            rel_min_x = min(p.x for p in pattern)
            rel_min_y = min(p.y for p in pattern)

            origin = GridPosition(min_x - rel_min_x, min_y - rel_min_y)

        translated: List[GridPosition] = []
        for rel in pattern:
            translated.append(GridPosition(origin.x + rel.x, origin.y + rel.y))

        self._activationPattern = translated
        self._endPhase = True
        
    def endTurn(self) -> None:
        self._activatedThisTurn.clear()
        self._canBeActivatedThisTurn.clear()

    def state(self) -> str:
        positions_sorted = sorted(self._positions.items(), key=lambda item: (item[0].x, item[0].y))
        pos_strs = [f"({pos.x},{pos.y})" for pos, _ in positions_sorted]

        pattern_sorted = sorted(self._canBeActivatedThisTurn, key=lambda p: (p.x, p.y))
        pattern_strs = [f"({p.x},{p.y})" for p in pattern_sorted]

        activated_sorted = sorted(self._activatedThisTurn, key=lambda p: (p.x, p.y))
        activated_strs = [f"({p.x},{p.y})" for p in activated_sorted]

        return (
            "Used positions: " + ", ".join(pos_strs)
            + "\nCan be activated this turn: " + ", ".join(pattern_strs)
            + "\nActivated this turn: " + ", ".join(activated_strs)
        )