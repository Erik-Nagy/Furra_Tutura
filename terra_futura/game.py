from typing import Optional
from .player import Player
from .simple_types import GameState, Deck, CardSource, GridPosition, Resource
from .interfaces import TerraFuturaInterface, GameObserverInterface, InterfacePile, InterfaceMoveCard, ProcessActionInterface, ProcessActionAssistanceInterface, InterfaceSelectReward
from .grid import Grid

class Game(TerraFuturaInterface):
    _state: GameState
    _players: list[Player]
    _piles: dict[Deck, InterfacePile]
    _turnNumber: int = 0
    _gameObserver: GameObserverInterface
    _moveCard: InterfaceMoveCard
    _processAction: ProcessActionInterface
    _processActionAssistance: ProcessActionAssistanceInterface
    _selectReward: InterfaceSelectReward

    def __init__(self, players: list[Player], piles: dict[Deck, InterfacePile], 
                 moveCard: InterfaceMoveCard, processAction: ProcessActionInterface, 
                 processActionAssistance: ProcessActionAssistanceInterface, 
                 selectReward: InterfaceSelectReward, gameObserver: GameObserverInterface) -> None:
        
        
        if len(players) < 2 or len(players) > 4:
            raise ValueError("Number of players not in interval 2..4")
        if len(piles) != 2:
            raise ValueError("Wrong number of decks")
            
        self._players: list[Player] = players.copy()
        self._piles = piles
        self._moveCard = moveCard
        self._processAction = processAction
        self._processActionAssistance = processActionAssistance
        self._selectReward = selectReward
        self._gameObserver = gameObserver
        self._assistanceUsed: bool = False

        self._state = GameState.TakeCardNoCardDiscarded
        self._onTurn: int = 0         # Index of the player in self.players whose turn it is
        self._turnNumber: int = 1
        self._moveCard = moveCard

    
    @property
    def currentPlayerId(self) -> int:
        return self._players[self._onTurn].id
    
    @property
    def state(self) -> GameState:
        return self._state
    
    @property
    def turnNumber(self) -> int:
        return self._turnNumber
    
    @property
    def players(self) -> list[Player]:
        return self._players
    
    def _getPlayer(self, id: int) -> Optional[Player]:
        for player in self._players:
            if player.id == id:
                return player
        return None
    
    def onTurn(self) -> int:
        return self._players[self._onTurn].id
    
    def isPlayerOnTurn(self, playerId: int) -> bool:
        return playerId == self.onTurn()
    
    def _advanceTurn(self) -> None:
        self._onTurn = (self._onTurn + 1) % len(self._players)
        if self._onTurn == 0:
            self._turnNumber += 1

    def _notifyObservers(self) -> None:
        state: dict[int, str] = {}
        for player in self.players:
            state[player.id] = self._getPlayerState(player.id)
        
        self._gameObserver.notifyAll(state)

    def _getPlayerState(self, player_id: int) -> str:
        player = self._getPlayer(player_id)
        if player is None:
            return "{}"
        grid_state = player.grid.state()
        return f'{{"state": "{self._state.value}", "on_turn": {self.onTurn}, "turn": {self.turnNumber}, "grid": {grid_state}}}'

    def discardLastCardFromDeck(self, playerId: int, deck: Deck) -> bool:
        if not self.isPlayerOnTurn(playerId):
            return False
        
        if self.state != GameState.TakeCardNoCardDiscarded:
            return False
        
        pile = self._piles.get(deck)
        if pile is None:
            # maybe not needed
            return False
        
        pile.removeLastCard()
        self._state = GameState.TakeCardCardDiscarded
        self._notifyObservers()
        return True
    
    def takeCard(self, playerId: int, source: CardSource, cardIndex: int, destination: GridPosition) -> bool:
        if not self.isPlayerOnTurn(playerId):
            return False
        
        if self._state not in {
            GameState.TakeCardNoCardDiscarded,
            GameState.TakeCardCardDiscarded,
        }:
            return False
        
        pile = self._piles.get(source.deck)
        if pile is None:
            return False
        
        player = self._getPlayer(playerId)
        if player is None:
            return False
        
        grid = player.grid

        if not self._moveCard.moveCard(pile, cardIndex, destination, grid):
            return False
        
        self._state = GameState.ActivateCard
        self._notifyObservers()
        return True
    
    def activateCard(self, playerId: int, card: GridPosition, 
                     inputs: list[tuple[Resource, GridPosition]], 
                     outputs: list[tuple[Resource, GridPosition]], 
                     pollution: list[GridPosition], otherPlayerId: int | None, 
                     otherCard: GridPosition | None) -> None:
        if not self.isPlayerOnTurn(playerId):
            return
        
        if self._state != GameState.ActivateCard:
            return
        
        player = self._getPlayer(playerId)
        if player is None:
            return
        
        grid = player.grid
        
        card_obj = grid.getCard(card)
        if card_obj is None:
            return
        
        isAssistance = otherPlayerId is not None and otherCard is not None
        if isAssistance:
            assert otherPlayerId != None # why do i need to assert?
            assert otherCard != None # why do i need to assert?
            
            otherPlayer = self._getPlayer(otherPlayerId)
            if otherPlayer is None:
                return
            
            otherGrid = otherPlayer.grid

            assisting_card = otherGrid.getCard(otherCard)

            if assisting_card is None:
                return
            
            if not self._processActionAssistance.activateCard(
                card_obj,
                grid,
                otherPlayer,
                assisting_card,
                inputs,
                outputs,
                pollution
            ):
                return
            
            self._assistanceUsed = True
            self._state = GameState.SelectReward
        else:
            if not self._processAction.activateCard(
                card_obj,
                grid,
                inputs,
                outputs,
                pollution,
            ):
                return
        
        self._notifyObservers()

    def selectReward(self, playerId: int, resource: Resource) -> None:
        if self._state != GameState.SelectReward:
            return
        
        if self._selectReward.player != playerId:
            return

        if not self._selectReward.canSelectReward(resource):
            return
        
        self._selectReward.selectReward(resource)
        
        self._state = GameState.ActivateCard
        self._notifyObservers()
        return
    
    def turnFinished(self, playerId: int) -> bool:
        if not self.isPlayerOnTurn(playerId):
            return False
        
        if self._state != GameState.ActivateCard:
            return False
        
        player = self._getPlayer(playerId)
        if player is None:
            return False
        grid = player.grid

        grid.endTurn()
        
        if self._turnNumber < 9:
            self._state = GameState.TakeCardNoCardDiscarded
            self._advanceTurn()
        elif self._turnNumber == 9:
            # Last regular turn
            self._advanceTurn()
            if self._onTurn == 0:
                self._state = GameState.SelectActivationPattern
            else:
                self._state = GameState.TakeCardNoCardDiscarded
        else:
            self._advanceTurn()
            if self._onTurn == 0:
                self._state = GameState.SelectScoringMethod
            else:
                self._state = GameState.SelectActivationPattern

        self._notifyObservers()
        return True

    def selectActivationPattern(self, playerId: int, card: int) -> bool:
        if not self.isPlayerOnTurn(playerId):
            return False
        
        if self._state != GameState.SelectActivationPattern:
            return False

        if card not in {0, 1}:
            return False
        
        player = self._getPlayer(playerId)
        if player is None:
            return False
        player.activation_patterns[card].select()
        self._state = GameState.ActivateCard
        
        self._notifyObservers()
        return True

    def selectScoring(self, playerId: int, card: int) -> bool:
        if not self.isPlayerOnTurn(playerId):
            return False
        
        if self._state != GameState.SelectScoringMethod:
            return False
        
        if card not in {0, 1}:
            return False
        
        player = self._getPlayer(playerId)
        if player is None:
            return False

        scoring_method = player.scoring_methods[card]
        scoring_method.selectThisMethodAndCalculate()

        self._advanceTurn()
        if self._onTurn == 0:
            self._state = GameState.Finish

        self._notifyObservers()
        return True
