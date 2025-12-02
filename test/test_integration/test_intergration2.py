# Integration test: basic two-player flow style-matched

from terra_futura.activation_pattern import ActivationPattern
from terra_futura.arbitrary_basic import ArbitraryBasic
from terra_futura.card import Card
from terra_futura.game import Game
from terra_futura.game_observer import TerraFuturaObserverInterface, GameObserver
from terra_futura.grid import Grid
from terra_futura.interfaces import Effect, InterfaceCard, InterfacePile
from terra_futura.move_card import MoveCard
from terra_futura.pile import Pile
from terra_futura.process_action import ProcessAction
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.player import Player
from terra_futura.scoring_method import ScoringMethod
from terra_futura.select_reward import SelectReward
from terra_futura.simple_types import *
from terra_futura.transformation_fixed import TransformationFixed
from typing import cast


class IntegrationObserver(TerraFuturaObserverInterface):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, game_state: str) -> None:
        self.messages.append(game_state)


def build_card(upper_effect: Effect | None = None,
               lower_effect: Effect | None = None,
               pollution_spaces: int = 0) -> Card:
    return Card(pollutionSpacesL=pollution_spaces, upperEffect=upper_effect, lowerEffect=lower_effect)


def build_player(player_id: int, grid: Grid) -> Player:
    ap1 = ActivationPattern(grid, [GridPosition(0, 0), GridPosition(0, 1), GridPosition(1, 0), GridPosition(1, 1)])
    ap2 = ActivationPattern(grid, [GridPosition(0, 0), GridPosition(1, 1), GridPosition(2, 0), GridPosition(0, 2)])

    sm1 = ScoringMethod([Resource.RED], Points(5), grid)
    sm2 = ScoringMethod([Resource.GREEN, Resource.GREEN], Points(10), grid)

    return Player(id=player_id, activation_patterns=[ap1, ap2], scoring_methods=[sm1, sm2], grid=grid)


def test_full_game() -> None:
    # Starting cards
    origin_a = build_card(upper_effect=ArbitraryBasic(from_=0, to=[Resource.RED], pollution=0), pollution_spaces=0)
    origin_b = build_card(upper_effect=ArbitraryBasic(from_=0, to=[Resource.GREEN], pollution=0), pollution_spaces=0)

    # Build level I cards
    deck_i_cards: list[InterfaceCard] = []
    for i in range(6):
        deck_i_cards.append(build_card(upper_effect=ArbitraryBasic(from_=0, to=[Resource.YELLOW], pollution=0), pollution_spaces=i % 4))
    for i in range(6):
        deck_i_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.RED], pollution=0),
            lower_effect=TransformationFixed(from_=[Resource.RED, Resource.RED], to=[Resource.GOODS], pollution=1),
            pollution_spaces=i % 3
        ))
    for i in range(6):
        deck_i_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.GREEN], pollution=0),
            lower_effect=TransformationFixed(from_=[Resource.GREEN], to=[Resource.FOOD], pollution=0),
            pollution_spaces=2 if i % 2 == 0 else 0
        ))

    # Build level II cards
    deck_ii_cards: list[InterfaceCard] = []
    for i in range(18):
        deck_ii_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.YELLOW], pollution=0),
            lower_effect=TransformationFixed(from_=[Resource.YELLOW], to=[Resource.CONSTRUCTION], pollution=0),
            pollution_spaces=1 if i % 3 == 0 else 0
        ))

    # Piles (seeded)
    deck_i = Pile(deck_i_cards, seed=42)
    deck_ii = Pile(deck_ii_cards, seed=42)

    # Grids and players
    grid1 = Grid()
    grid2 = Grid()

    grid1.putCard(GridPosition(0, 0), origin_a)
    grid2.putCard(GridPosition(0, 0), origin_b)

    # Reset activation bookkeeping via public API
    grid1.endTurn()
    grid2.endTurn()

    player_a = build_player(1, grid1)
    player_b = build_player(2, grid2)

    # Handlers
    mover = MoveCard()
    action_handler = ProcessAction()
    assist_handler = ProcessActionAssistance()
    reward_picker = SelectReward()

    # Observers
    obs_a = IntegrationObserver()
    obs_b = IntegrationObserver()
    game_observer = GameObserver({1: obs_a, 2: obs_b})

    # Game instance
    game = Game(players=[player_a, player_b],
                piles={Deck.LEVEL_I: cast(InterfacePile, deck_i), Deck.LEVEL_II: cast(InterfacePile, deck_ii)},
                moveCard=mover, processAction=action_handler, processActionAssistance=assist_handler,
                selectReward=reward_picker, gameObserver=game_observer)

    # Initial assertions
    assert game.state == GameState.TakeCardNoCardDiscarded
    assert game.turnNumber == 1
    assert game.currentPlayerId == 1

    # Turn 1: player A place to the right
    ok = game.takeCard(playerId=1, source=CardSource(Deck.LEVEL_I, 1), cardIndex=1, destination=GridPosition(1, 0))
    if not ok:
        game.discardLastCardFromDeck(1, Deck.LEVEL_I)
        ok = game.takeCard(playerId=1, source=CardSource(Deck.LEVEL_I, 1), cardIndex=1, destination=GridPosition(1, 0))
    assert ok
    game.turnFinished(1)

    # Turn 2: player B
    ok = game.takeCard(playerId=2, source=CardSource(Deck.LEVEL_I, 2), cardIndex=2, destination=GridPosition(1, 0))
    assert ok
    game.turnFinished(2)

    # Continue building to fill 3x3
    remaining = [GridPosition(2, 0), GridPosition(0, 1), GridPosition(1, 1), GridPosition(2, 1), GridPosition(0, 2), GridPosition(1, 2), GridPosition(2, 2)]
    for pos in remaining:
        game.takeCard(playerId=1, source=CardSource(Deck.LEVEL_I, 1), cardIndex=1, destination=pos)
        game.turnFinished(1)
        game.takeCard(playerId=2, source=CardSource(Deck.LEVEL_II, 1), cardIndex=1, destination=pos)
        game.turnFinished(2)

    # Verify completion
    assert len(grid1._positions) == 9
    assert len(grid2._positions) == 9

    print(f"Turn number: {game.turnNumber}, State: {game.state}")

    # Final checks
    assert game.turnNumber == 9
    assert len(grid1._positions) == 9
    assert len(grid2._positions) == 9

    assert len(obs_a.messages) > 0
    assert len(obs_b.messages) > 0

    for pos in grid1._positions.keys():
        assert -2 <= pos.x <= 2
        assert -2 <= pos.y <= 2

    upper_count = sum(1 for c in grid1._positions.values() if c.upperEffect is not None)
    lower_count = sum(1 for c in grid1._positions.values() if c.lowerEffect is not None)
    assert upper_count > 0
    assert lower_count > 0
