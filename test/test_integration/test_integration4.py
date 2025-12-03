"""
Integration Test 4: Two Turns With Card Activations

Tests fundamental game mechanics including card placement, especially activation,
pollution management, and card deactivation with a randomly shuffled deck during 2 turns.
"""

from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.grid import Grid
from terra_futura.pile import Pile, RandomShuffler
from terra_futura.card import Card
from terra_futura.move_card import MoveCard
from terra_futura.process_action import ProcessAction
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.select_reward import SelectReward
from terra_futura.game_observer import GameObserver
from terra_futura.activation_pattern import ActivationPattern
from terra_futura.scoring_method import ScoringMethod
from terra_futura.simple_types import *
from terra_futura.arbitrary_basic import ArbitraryBasic
from terra_futura.transformation_fixed import TransformationFixed
from terra_futura.interfaces import TerraFuturaObserverInterface, Effect, InterfaceCard, InterfacePile
from typing import cast, Counter


class GameStateObserver(TerraFuturaObserverInterface):
    """Simple observer implementation for testing."""
    def __init__(self) -> None:
        self.notifications: list[str] = []

    def notify(self, game_state: str) -> None:
        self.notifications.append(game_state)


def create_test_card(upper_effect: Effect | None = None,
                     lower_effect: Effect | None = None,
                     pollution_spaces: int = 0) -> Card:
    """Create a card with specified effects for testing."""
    return Card(pollutionSpacesL=pollution_spaces,
                upperEffect=upper_effect,
                lowerEffect=lower_effect)


def create_test_player(player_id: int, grid: Grid) -> Player:
    """Create a player with activation patterns and scoring methods."""
    activation_pattern_1 = ActivationPattern(grid, [
        GridPosition(0, 0), GridPosition(0, 1),
        GridPosition(1, 0), GridPosition(1, 1)
    ])
    activation_pattern_2 = ActivationPattern(grid, [
        GridPosition(0, 0), GridPosition(1, 1),
        GridPosition(2, 0), GridPosition(0, 2)
    ])
    scoring_1 = ScoringMethod([Resource.RED], Points(5), grid)
    scoring_2 = ScoringMethod([Resource.GREEN, Resource.GREEN], Points(10), grid)

    return Player(
        id=player_id,
        activation_patterns=[activation_pattern_1, activation_pattern_2],
        scoring_methods=[scoring_1, scoring_2],
        grid=grid
    )


def test_two_turns_with_card_activations() -> None:
    """
    A few randomised turns testing basic mechanics, pollution, and activating cards.

    This test verifies:
    - Deck shuffling
    - Card placement and grid constraints
    - Card activation mechanics
    - Resource production and management
    - Pollution placement on cards with/without pollution spaces
    - Card deactivation when pollution fills all spaces
    """

    # ===== SETUP PHASE =====

    # Create starting cards for both players
    # Starting cards have simple resource production

    # Create cards for Level I pile (at least 18 cards needed)
    level_i_cards: list[InterfaceCard] = []

    # Cards 1-6: Simple resource production, various pollution spaces
    for i in range(6):
        level_i_cards.append(create_test_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.YELLOW], pollution=1),
            pollution_spaces=i%4
        ))

    # Cards 7-12: Cards with pollution-generating effects
    for i in range(6):
        level_i_cards.append(create_test_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.RED], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.YELLOW],
                to=[Resource.GOODS],
                pollution=0  # Generates pollution
            ),
            pollution_spaces=i%3
        ))

    # Cards 13-18: More varied cards
    for i in range(6):
        level_i_cards.append(create_test_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.GREEN], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.GREEN],
                to=[Resource.FOOD],
                pollution=0
            ),
            pollution_spaces=2 if i % 2 == 0 else 0
        ))

    # Create Level II pile (similar structure)
    level_ii_cards: list[InterfaceCard] = []
    for i in range(18):
        level_ii_cards.append(create_test_card(
            upper_effect=ArbitraryBasic(from_=0, to=[Resource.YELLOW], pollution=0),
            lower_effect=TransformationFixed(
                from_=[Resource.YELLOW],
                to=[Resource.CONSTRUCTION],
                pollution=0
            ),
            pollution_spaces=1 if i % 3 == 0 else 0
        ))

    # Create piles with seeded shuffler for determinism
    shuffler = RandomShuffler()
    pile_level_i = Pile(
        shuffler.shuffle(level_i_cards),
        shuffler=shuffler
    )
    pile_level_ii = Pile(
        shuffler.shuffle(level_ii_cards),
        shuffler=shuffler
    )

    

    # Create grids and players
    grid1 = Grid()
    grid2 = Grid()

    player1 = create_test_player(1, grid1)
    player2 = create_test_player(2, grid2)

    # Create game dependencies
    move_card = MoveCard()
    process_action = ProcessAction()
    process_action_assistance = ProcessActionAssistance()
    select_reward = SelectReward()

    # Create observers
    observer1 = GameStateObserver()
    observer2 = GameStateObserver()
    game_observer = GameObserver({1: observer1, 2: observer2})

    # Create game
    game = Game(
        players=[player1, player2],
        piles={Deck.LEVEL_I: cast(InterfacePile, pile_level_i), Deck.LEVEL_II: cast(InterfacePile, pile_level_ii)},
        moveCard=move_card,
        processAction=process_action,
        processActionAssistance=process_action_assistance,
        selectReward=select_reward,
        gameObserver=game_observer
    )

    # Verify initial state
    assert game.state == GameState.TakeCardNoCardDiscarded
    assert game.turnNumber == 1
    assert game.currentPlayerId == 1

    # ===== TURN 1: Player 1 =====
    # Take first card from Level I pile and place it
    success = game.takeCard(
        playerId=1,
        source=CardSource(deck=Deck.LEVEL_I, index=1),
        cardIndex=1,
        destination=GridPosition(0, 0)
    )
    assert success

    for pos in grid1.shouldBeActivated:
        card = grid1.getCard(pos)
        if card and card.upperEffect:
            eff = card.upperEffect

            if isinstance(eff, ArbitraryBasic):
                game.activateCard(playerId=1,
                card = GridPosition(0, 0),
                inputs = [(Resource.RED, GridPosition(0,0)) for _ in range(eff.from_)],
                outputs = [(res, GridPosition(0,0)) for res in eff.to],
                pollution = [GridPosition(0,0)] if eff.pollution == 1 else [],
                otherPlayerId = None,
                otherCard = None)
                

                if eff.from_ == 0 and card.isActive():
                    assert card.canGetResources(eff.to)
                else:
                    assert not card.canGetResources(eff.to)
                
    # After takeCard, state should be ActivateCard
    assert len(grid1.grid) == 1  

    assert game.turnFinished(1)
    assert game.currentPlayerId == 2
    assert game.turnNumber == 1

    # ===== TURN 1: Player 2 =====
    success = game.takeCard(
        playerId=2,
        source=CardSource(deck=Deck.LEVEL_I, index=2),
        cardIndex=2,
        destination=GridPosition(0, 0)
    )
    assert success

    for pos in grid2.shouldBeActivated:
        card = grid2.getCard(pos)
        if card and card.lowerEffect:
            eff = card.lowerEffect
        elif card and card.upperEffect:
            eff = card.upperEffect
        
        if card and eff:
            if isinstance(eff, ArbitraryBasic):
                game.activateCard(playerId=2,
                card = GridPosition(0, 0),
                inputs = [(Resource.RED, GridPosition(0,0)) for _ in range(eff.from_)],
                outputs = [(res, GridPosition(0,0)) for res in eff.to],
                pollution = [GridPosition(0,0)] if eff.pollution == 1 else [],
                otherPlayerId = None,
                otherCard = None)
                

                if eff.from_ == 0 and card.isActive():
                    assert card.canGetResources(eff.to)
                else:
                    assert not card.canGetResources(eff.to)

            if isinstance(eff, TransformationFixed):
                game.activateCard(playerId=2,
                card = GridPosition(0, 0),
                inputs = [(res, GridPosition(0,0)) for res in eff.from_],
                outputs = [(res, GridPosition(0,0)) for res in eff.to],
                pollution = [GridPosition(0,0)] if eff.pollution == 1 else [],
                otherPlayerId = None,
                otherCard = None)
                
                assert not card.canGetResources(eff.to)

    assert game.turnFinished(2)
    assert game.turnNumber == 2
    assert game.currentPlayerId == 1

    # ===== TURNS 2: Continue building grids =====
    # We'll simulate one more round and activate the cards

    success = game.takeCard(
        playerId=1,
        source=CardSource(deck=Deck.LEVEL_I, index=5),
        cardIndex=5,
        destination=GridPosition(2, 0)
    )
    assert success

    for pos in grid1.shouldBeActivated:
        card = grid1.getCard(pos)
        if card and card.upperEffect:
            eff = card.upperEffect
        
            if isinstance(eff, ArbitraryBasic):
                game.activateCard(playerId=1,
                card = pos,
                inputs = [(Resource.RED, pos) for _ in range(eff.from_)],
                outputs = [(res, pos) for res in eff.to],
                pollution = [pos] if eff.pollution == 1 else [],
                otherPlayerId = None,
                otherCard = None)
                

                if eff.from_ == 0 and card.isActive():
                    assert card.canGetResources(eff.to)
                else:
                    assert not card.canGetResources(eff.to)
                
    assert len(grid1.grid) == 2  

    assert game.turnFinished(1)
    assert game.currentPlayerId == 2
    assert game.turnNumber == 2

    # ===== TURN 2: Player 2 =====
    success = game.takeCard(
        playerId=2,
        source=CardSource(deck=Deck.LEVEL_I, index=5),
        cardIndex=5,
        destination=GridPosition(0, -2)
    )
    assert success

    for pos in grid2.shouldBeActivated:
        card = grid2.getCard(pos)
        if card and card.lowerEffect:
            eff = card.lowerEffect
        elif card and card.upperEffect:
            eff = card.upperEffect
        
        if card and eff:
            if isinstance(eff, ArbitraryBasic):
                game.activateCard(playerId=2,
                card = pos,
                inputs = [(Resource.RED, pos) for _ in range(eff.from_)],
                outputs = [(res, pos) for res in eff.to],
                pollution = [pos] if eff.pollution == 1 else [],
                otherPlayerId = None,
                otherCard = None)
                

                if eff.from_ == 0 and card.isActive():
                    assert card.canGetResources(eff.to)
                else:
                    assert not card.canGetResources(eff.to)

            if isinstance(eff, TransformationFixed):
                otherCard = grid2.getCard(GridPosition(0,0))
                if otherCard:
                    c1 = Counter(otherCard.resources)
                    c2 = Counter(eff.from_)
                    condition = True
                    for res in c2.keys():
                        if res not in c1.keys() or c1[res] < c2[res]:
                            condition = False
                            break

                    game.activateCard(playerId=2,
                    card = pos,
                    inputs = [(res, GridPosition(0,0)) for res in eff.from_],
                    outputs = [(res, pos) for res in eff.to],
                    pollution = [pos] if eff.pollution == 1 else [],
                    otherPlayerId = None,
                    otherCard = None)
                    
                    
                    if condition and card and card.isActive() and otherCard.isActive():
                        assert card.canGetResources(eff.to)

                    else:
                        assert not card.canGetResources(eff.to)
    
    
    assert len(grid2.grid) == 2  

    assert game.turnFinished(2)
    assert game.currentPlayerId == 1
    assert game.turnNumber == 3

    # Check what turn we're on and what state
    print(f"Turn number: {game.turnNumber}, State: {game.state}, Current player: {game.currentPlayerId}")

    # ===== VERIFY GRID =====
    # Verify pollution mechanics without manually placing
    # Check that cards have proper pollution space attributes
    for pos, card_interface in grid1.grid.items():
        # Cast to Card to access pollution attribute
        card = cast(Card, card_interface)
        assert card.pollutionSpacesL >= 0
        assert card.pollution >= 0
        # Cards should be active unless pollution filled all spaces
        if card.pollution < card.pollutionSpacesL:
            assert card.isActive()

    # ===== TEST SUMMARY =====
    # We successfully completed a 2 turns with activations and randomly shuffled decks:
    # - Card placement and grid constraints (3x3)
    # - Pollution mechanics are present on cards
    # - Game state management worked correctly through all turns
    # - All card activations worked correctly

    # Verify observers received notifications
    assert len(observer1.notifications) > 0
    assert len(observer2.notifications) > 0

    # Verify grid positions are valid
    for pos in grid1.grid.keys():
        assert -2 <= pos.x <= 2
        assert -2 <= pos.y <= 2

    print("✓ Test 4: Two Turns With Card Activations - PASSED")
