from typing import Dict, Optional
from terra_futura.interfaces import TerraFuturaObserverInterface

class GameObserver:
    _observers: Dict[int, TerraFuturaObserverInterface] = {}
    def __init__(self, observers: Optional[Dict[int, TerraFuturaObserverInterface]] = None) -> None:
        if observers is not None:
            self._observers: dict[int, TerraFuturaObserverInterface] = observers

    @property
    def observers(self) -> Dict[int, TerraFuturaObserverInterface]:
        return self._observers.copy()
        
    def notifyAll(self, newState: Dict[int, str]) -> None:
        for player_id in newState:
            if player_id in self._observers:
                self._observers[player_id].notify(newState[player_id])
    
    def register_observer(self, player_id: int, observer: TerraFuturaObserverInterface) -> None:
        self._observers[player_id] = observer

    def unregister_observer(self, player_id: int) -> None:
        if player_id in self._observers:
            del self._observers[player_id]

    def notify(self, game_state: str) -> None:
        for observer in self._observers.values():
            observer.notify(game_state)
