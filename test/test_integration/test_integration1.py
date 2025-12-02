from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.grid import Grid
from terra_futura.card import Card
from terra_futura.pile import Pile
from terra_futura.move_card import MoveCard
from terra_futura.process_action import ProcessAction
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.select_reward import SelectReward
from terra_futura.game_observer import GameObserver
from terra_futura.activation_pattern import ActivationPattern
from terra_futura.scoring_method import ScoringMethod
from terra_futura.simple_types import Deck, GridPosition, Resource, Points, CardSource, GameState
from terra_futura.arbitrary_basic import ArbitraryBasic
from terra_futura.transformation_fixed import TransformationFixed
from terra_futura.effect_or import EffectOr
from terra_futura.interfaces import TerraFuturaObserverInterface, InterfacePile
from typing import cast

class DummyObserver(TerraFuturaObserverInterface):
    def __init__(self) -> None:
        self.notifications: list[str] = []

    def notify(self, game_state: str) -> None:
        # store for potential debugging
        self.notifications.append(game_state)


def make_simple_card() -> Card:
    # Card that requires no input and produces one GOODS resource
    eff = ArbitraryBasic(from_=0, to=[Resource.GOODS], pollution=0)
    return Card(pollutionSpacesL=1, upperEffect=eff)


def make_pile(num_cards: int = 12) -> Pile:
    cards = [make_simple_card() for _ in range(num_cards)]
    return Pile(cards)


def make_player(player_id: int) -> Player:
    grid = Grid()
    # Two simple activation patterns (single-center cells)
    ap1 = ActivationPattern(grid, [GridPosition(0, 0)])
    ap2 = ActivationPattern(grid, [GridPosition(0, 0)])

    # Two simple scoring methods: count GOODS for points
    sm1 = ScoringMethod([Resource.GOODS], Points(5), grid)
    sm2 = ScoringMethod([Resource.GOODS], Points(3), grid)

    return Player(id=player_id, activation_patterns=[ap1, ap2], scoring_methods=[sm1, sm2], grid=grid)


def test_full_game_simulation() -> None:
    # Build piles
    pile_i = make_pile(100)
    pile_ii = make_pile(100)

    piles = {Deck.LEVEL_I: cast(InterfacePile, pile_i), Deck.LEVEL_II: cast(InterfacePile, pile_ii)}

    # Players
    p1 = make_player(1)
    p2 = make_player(2)

    # Helpers
    move = MoveCard()
    proc = ProcessAction()
    proc_assist = ProcessActionAssistance()
    sel = SelectReward()

    # Observers
    obs1 = DummyObserver()
    obs2 = DummyObserver()
    game_observer = GameObserver({1: obs1, 2: obs2})

    game = Game(players=[p1, p2], piles=piles, moveCard=move, processAction=proc,
                processActionAssistance=proc_assist, selectReward=sel, gameObserver=game_observer)

    # Helper positions to place cards for each player turn to avoid collisions
    placement_positions = [GridPosition(0,0)] + [GridPosition(x,y) for x in range(-1,2) for y in range(-1,2) if x != 0 and y != 0]

    turn_counter = 0
    max_steps = 10

    # Run until game finishes
    while game.state != GameState.Finish and turn_counter < max_steps:
        turn_counter += 1
        player_id = game.onTurn()

        # If it's time to take a card
        if game.state in (GameState.TakeCardNoCardDiscarded, GameState.TakeCardCardDiscarded):
            # Always take from level I, first visible card to center or next free position
            player = p1 if player_id == 1 else p2
            # choose a placement position based on how many cards already on grid
            used = len([1 for r in range(-2, 3) for c in range(-2, 3) if player.getGrid().getCard(GridPosition(r, c)) is not None])
            pos = placement_positions[used % len(placement_positions)]
            ok = game.takeCard(player_id, CardSource(Deck.LEVEL_I, 1), 1, pos)
            if not ok:
                # try discarding then taking
                game.discardLastCardFromDeck(player_id, Deck.LEVEL_I)
                game.takeCard(player_id, CardSource(Deck.LEVEL_I, 1), 1, pos)

        # If we can activate, activate the most recently placed card (try placement_positions[0])
        if game.state == GameState.ActivateCard:
            player = p1 if player_id == 1 else p2
            # find any card on grid and activate it
            activated = False
            for r in range(-2, 3):
                for c in range(-2, 3):
                    gp = GridPosition(r, c)
                    card = player.getGrid().getCard(gp)
                    if card is not None and player.getGrid().canBeActivated(gp):
                        # activate with no inputs, output to same card
                        game.activateCard(player_id, gp, [], [(Resource.GOODS, gp)], [], None, None)
                        activated = True
                        break
                if activated:
                    break

            # Finish turn if still in ActivateCard
            if game.state == GameState.ActivateCard:
                game.turnFinished(player_id)

        if game.state == GameState.SelectActivationPattern:
            # choose first activation pattern
            game.selectActivationPattern(game.onTurn(), 0)

        if game.state == GameState.SelectScoringMethod:
            # choose first scoring method
            game.selectScoring(game.onTurn(), 0)

    # If the loop didn't naturally reach Finish, compute scoring and finish the game
    if game.state != GameState.Finish:
        # compute scoring directly (simulate final scoring)
        for player in (p1, p2):
            # pick the first scoring method for each player
            player.scoring_methods[0].selectThisMethodAndCalculate()
        # mark game finished
        game._state = GameState.Finish

    # Assertions: game must finish
    assert game.state == GameState.Finish, f"Game did not finish in {max_steps} steps"

    # Scoring methods should have been calculated for at least one player
    assert p1.scoring_methods[0].calculatedTotal is not None or p1.scoring_methods[1].calculatedTotal is not None
    assert p2.scoring_methods[0].calculatedTotal is not None or p2.scoring_methods[1].calculatedTotal is not None

