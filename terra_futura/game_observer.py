from typing import Dict
from abc import ABC
from terra_futura.interfaces import TerraFuturaObserverInterface
from typing import Dict

class GameObserver:
    def __init__(self, observers: Dict[int, TerraFuturaObserverInterface]) -> None:
        self._observers = observers

    @property
    def observers(self) ->Dict[int, TerraFuturaObserverInterface]:
        return self._observers.copy()
        
    def notifyAll(self, newState: Dict[int, str]) -> None:
        for player_id in newState:
            if player_id in self._observers:
                self._observers[player_id].notify(newState[player_id])
    

