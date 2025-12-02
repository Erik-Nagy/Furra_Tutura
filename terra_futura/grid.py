from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from typing import Optional, List
from terra_futura.simple_types import *

class Grid (InterfaceGrid):
    def __init__(self) ->None:
        self.grid: dict[GridPosition, InterfaceCard] = {}
        self.shouldBeActivated: set[GridPosition] = set()
        self.minY = self.maxY = self.minX = self.maxX = 0
        self.activationPattern: list[GridPosition] = []
    
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        return self.grid.get(coordinate, None)

    def canPutCard(self, coordinate: GridPosition)-> bool:
        if self.getCard(coordinate) != None:
            return False
        
        if self.shouldBeActivated != set():
            return False
        
        if max(self.maxX, coordinate.x) - min(self.minX, coordinate.x) >= 3:
            return False
        
        if max(self.maxY, coordinate.y) - min(self.minY, coordinate.y) >= 3:
            return False
        
        return True

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        if list(self.grid.keys()) == [] and (coordinate.x != 0 or coordinate.y != 0):
            raise ValueError("First card must be placed on Grid position (0,0)")

        if self.canPutCard(coordinate):
            self.grid[coordinate] = card
            self.shouldBeActivated.clear()
            for i in range(-2, 3):
                card1 = self.getCard(GridPosition(coordinate.x, i))
                if card1:
                    self.shouldBeActivated.add(GridPosition(coordinate.x, i))

                card2 = self.getCard(GridPosition(i, coordinate.y))
                if card2:
                    self.shouldBeActivated.add(GridPosition(i, coordinate.y))

            self.minX = min(self.minX, coordinate.x)
            self.maxX = max(self.maxX, coordinate.x)
            self.minY = min(self.minY, coordinate.y)
            self.maxY = max(self.maxY, coordinate.y)
        else:
            raise ValueError("Cant put a card there")

    def canBeActivated(self, coordinate: GridPosition)-> bool:
        return coordinate in self.shouldBeActivated
        
    def setActivated(self, coordinate: GridPosition) -> None:
        if self.canBeActivated(coordinate):
            self.shouldBeActivated.remove(coordinate)
        else:
            raise ValueError("Cannot activate this position")


    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        self.activationPattern = pattern.copy()
        
    def endTurn(self) -> None:
        self.shouldBeActivated.clear()

    def state(self) -> str:
        positions_strs: list[str] = []
        for x in range(-2, 3):
            for y in range(-2, 3):
                if self.getCard(GridPosition(x,y)) != None:
                    positions_strs.append(f"({x},{y})")

        pattern_sorted = sorted(self._activationPattern, key=lambda p: (p.x, p.y))
        pattern_strs = [f"({p.x},{p.y})" for p in pattern_sorted]

        activated_sorted = sorted(self._activatedThisTurn, key=lambda p: (p.x, p.y))
        activated_strs = [f"({p.x},{p.y})" for p in activated_sorted]
        
        return (
            "Used positions: " + ", ".join(positions_strs)
            + "\nActivation pattern: " + ", ".join(pattern_strs)
            + "\nActivated this turn: " + ", ".join(activated_strs)
        )