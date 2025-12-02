# Integration test: two-player full game

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

def build_player(player_id: int, grid: Grid) -> Player:
    pattern_one = ActivationPattern(grid, [GridPosition(0, 0), GridPosition(0, 1), GridPosition(1, 0), GridPosition(1, 1)])
    pattern_two = ActivationPattern(grid, [GridPosition(0, 0), GridPosition(1, 1), GridPosition(2, 0), GridPosition(0, 2)])

    score_rule_a = ScoringMethod([Resource.GOODS, Resource.FOOD], Points(15), grid)
    score_rule_b = ScoringMethod([Resource.RED, Resource.GREEN, Resource.YELLOW], Points(8), grid)

    return Player(id=player_id, activation_patterns=[pattern_one, pattern_two], scoring_methods=[score_rule_a, score_rule_b], grid=grid)

def build_card(upper_effect: Effect | None = None,
               lower_effect: Effect | None = None,
               pollution_spaces: int = 0) -> Card:
    return Card(pollutionSpacesL=pollution_spaces,
                upperEffect=upper_effect,
                lowerEffect=lower_effect)

def test_full_game() -> None:
    # Starting cards produce initial resources
    origin_a = build_card(
        upper_effect=ArbitraryBasic(from_=0, to=[Resource.RED, Resource.RED], pollution=0),
        pollution_spaces=1
    )
    origin_b = build_card(
        upper_effect=ArbitraryBasic(from_=0, to=[Resource.GREEN, Resource.GREEN], pollution=0),
        pollution_spaces=1
    )

    # Level I pile cards (transformations)
    deck_i_cards: list[InterfaceCard] = []

    # Cards 1-6: raw materials
    for i in range(6):
        resource = [Resource.RED, Resource.GREEN, Resource.YELLOW][i % 3]
        deck_i_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[resource], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.RED, Resource.GREEN],
                to=[Resource.GOODS],
                pollution=1
            ),
            pollution_spaces=2
        ))

    # Cards 7-12: more transforms
    for i in range(6):
        deck_i_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.YELLOW, Resource.YELLOW], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.GREEN, Resource.GREEN],
                to=[Resource.FOOD],
                pollution=0  # Clean transformation
            ),
            pollution_spaces=1
        ))

    # Cards 13-18: construction cards
    for i in range(6):
        deck_i_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.RED], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.YELLOW, Resource.YELLOW, Resource.YELLOW],
                to=[Resource.CONSTRUCTION],
                pollution=2  # More polluting
            ),
            pollution_spaces=3
        ))

    # Level II pile
    deck_ii_cards: list[InterfaceCard] = []
    for i in range(18):
        deck_ii_cards.append(build_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.GREEN, Resource.YELLOW], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.RED, Resource.YELLOW],
                to=[Resource.FOOD],
                pollution=0
            ),
            pollution_spaces=2
        ))

    # Piles (seeded)
    # Seed value used for shuffling
    deck_i = Pile(deck_i_cards, seed=123)
    deck_ii = Pile(deck_ii_cards, seed=123)

    # Grids and players
    grid1 = Grid()
    grid2 = Grid()

    # Place starting cards on grids
    grid1.putCard(GridPosition(0, 0), origin_a)
    grid2.putCard(GridPosition(0, 0), origin_b)

    # Use public endTurn() to reset activation bookkeeping
    grid1.endTurn()
    grid2.endTurn()

    player_a = build_player(1, grid1)
    player_b = build_player(2, grid2)

    # Game dependency handlers
    mover = MoveCard()
    action_handler = ProcessAction()
    assist_handler = ProcessActionAssistance()
    reward_picker = SelectReward()

    # Observers
    obs_a = IntegrationObserver()
    obs_b = IntegrationObserver()
    game_observer = GameObserver({1: obs_a, 2: obs_b})

    # Game instance
    game = Game(
        players=[player_a, player_b],
        piles={Deck.LEVEL_I: cast(InterfacePile, deck_i), Deck.LEVEL_II: cast(InterfacePile, deck_ii)},
        moveCard=mover,
        processAction=action_handler,
        processActionAssistance=assist_handler,
        selectReward=reward_picker,
        gameObserver=game_observer
    )

    # Verify initial game state
    assert game.state == GameState.TakeCardNoCardDiscarded
    assert game.turnNumber == 1
    assert game.currentPlayerId == 1

    # Turns 1-2: initial setup
    # Player A: first placement
    game.takeCard(playerId=1, source=CardSource(deck=Deck.LEVEL_I, index=1), cardIndex=1, destination=GridPosition(1, 0))
    # Activation skipped for brevity
    game.turnFinished(1)

    # Player B: first placement
    game.takeCard(playerId=2, source=CardSource(deck=Deck.LEVEL_I, index=2), cardIndex=2, destination=GridPosition(1, 0))
    game.turnFinished(2)
    assert game.turnNumber == 2

    # Turns 3-4: continue building
    # Turn 3: player A
    game.takeCard(
        playerId=1,
        source=CardSource(deck=Deck.LEVEL_II, index=1),
        cardIndex=1,
        destination=GridPosition(0, 1)
    )
    game.turnFinished(1)

    # Turn 4: player B
    game.takeCard(
        playerId=2,
        source=CardSource(deck=Deck.LEVEL_II, index=1),
        cardIndex=1,
        destination=GridPosition(0, 1)
    )
    game.turnFinished(2)

    # Turns 5-9: complete 3x3 grids
    # Already placed positions noted; need remaining positions below
    remaining_positions = [
        GridPosition(1, 1), GridPosition(2, 0), GridPosition(2, 1),
        GridPosition(0, 2), GridPosition(1, 2), GridPosition(2, 2)
    ]

    for pos in remaining_positions:
        # Player A places next
        game.takeCard(playerId=1, source=CardSource(deck=Deck.LEVEL_I, index=1), cardIndex=1, destination=pos)
        game.turnFinished(1)

        # Player B mirrors placement
        game.takeCard(playerId=2, source=CardSource(deck=Deck.LEVEL_II, index=1), cardIndex=1, destination=pos)
        game.turnFinished(2)

    # Verify grids are complete
    assert len(grid1._positions) == 9
    assert len(grid2._positions) == 9

    # Summary: completed game flow and validations

    # Final state checks
    assert game.turnNumber == 9
    assert len(grid1._positions) == 9
    assert len(grid2._positions) == 9

    # Observers received messages
    assert len(obs_a.messages) > 0
    assert len(obs_b.messages) > 0

    # Grid positions within expected bounds
    for pos in grid1._positions.keys():
        assert -2 <= pos.x <= 2
        assert -2 <= pos.y <= 2

    for pos in grid2._positions.keys():
        assert -2 <= pos.x <= 2
        assert -2 <= pos.y <= 2

    # Cards have expected effects
    cards_with_upper_effects = sum(1 for card in grid1._positions.values() if card.upperEffect is not None)
    cards_with_lower_effects = sum(1 for card in grid1._positions.values() if card.lowerEffect is not None)
    assert cards_with_upper_effects > 0
    assert cards_with_lower_effects > 0
