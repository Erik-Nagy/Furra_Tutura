from .simple_types import Resource, GridPosition
from .interfaces import InterfaceSelectReward, InterfaceCard, PlayerInterface
from typing import List, Optional

class SelectReward(InterfaceSelectReward):
    _player: Optional[PlayerInterface]
    selection: list[Resource]
    card: Optional[InterfaceCard]

    @property
    def player(self) -> Optional[PlayerInterface]:
        return self._player
    
    def __init__(self) -> None:
        self._player = None
    
    def setReward(self, player: PlayerInterface, card: InterfaceCard, reward: List[Resource]) ->None:
        hasCard = False
        grid = player.getGrid()
        for row in range(-2, 3):
            for col in range(-2, 3):
                c = grid.getCard(GridPosition(row, col))
                if c is not None and c.state() == card.state():
                    hasCard = True

        if hasCard and card.isActive():
            self._player = player
            self.selection = reward.copy()
            self.card = card

    
    
    def canSelectReward(self, resource: Resource) -> bool:
        if self.player == None:
            return False
        
        return resource in self.selection

    def selectReward(self, resource: Resource) -> None:
        if self.canSelectReward(resource) and self.card and self.card.isActive():
            self.card.putResources([resource])

    def state(self)-> str:
        if self.player == None:
            return f"Reward has not been set"
        return f"Player number {self.player.getId()} is picking from {self.selection}"