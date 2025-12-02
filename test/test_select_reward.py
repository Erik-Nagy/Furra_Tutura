import pytest
from terra_futura.select_reward import SelectReward
from terra_futura.card import Card
from terra_futura.grid import Grid
from terra_futura.simple_types import GridPosition, Resource, Points
from terra_futura.activation_pattern import ActivationPattern
from terra_futura.scoring_method import ScoringMethod
from terra_futura.player import Player


def make_player_with_grid(grid: Grid, pid: int) -> Player:
    ap1 = ActivationPattern(grid, [GridPosition(0, 0)])
    ap2 = ActivationPattern(grid, [GridPosition(0, 0)])
    sm1 = ScoringMethod([], Points(0), grid)
    sm2 = ScoringMethod([], Points(0), grid)
    return Player(id=pid, activation_patterns=[ap1, ap2], scoring_methods=[sm1, sm2], grid=grid)


def test_set_reward_not_set_when_no_matching_card_or_inactive() -> None:
    sr = SelectReward()

    assert sr.player is None
    assert not sr.canSelectReward(Resource.GOODS)
    assert sr.state() == "Reward has not been set"

    grid2 = Grid()
    inactive_card = Card()
    grid2.putCard(GridPosition(0, 0), inactive_card)
    player2 = make_player_with_grid(grid2, pid=8)

    sr2 = SelectReward()
    sr2.setReward(player2, Card(), [Resource.MONEY])
    assert sr2.player is None
    assert sr2.state() == "Reward has not been set"


def test_set_reward_success_and_select() -> None:
    sr = SelectReward()

    grid = Grid()
    grid_card = Card(pollutionSpacesL=1)
    grid.putCard(GridPosition(0, 0), grid_card)

    player = make_player_with_grid(grid, pid=3)

    passed_card = Card(pollutionSpacesL=1)
    reward_options = [Resource.GOODS, Resource.MONEY]

    sr.setReward(player, passed_card, reward_options)

    assert sr.player is player
    assert sr.canSelectReward(Resource.GOODS)
    assert sr.canSelectReward(Resource.MONEY)
    assert not sr.canSelectReward(Resource.FOOD)
    assert f"Player number {player.getId()} is picking from" in sr.state()
    assert passed_card.resources == []
    sr.selectReward(Resource.GOODS)
    assert Resource.GOODS in passed_card.resources

    before = list(passed_card.resources)
    sr.selectReward(Resource.FOOD)
    assert passed_card.resources == before

    passed_card.placePollution(1)
    sr.selectReward(Resource.MONEY)
    assert passed_card.resources == before
    assert passed_card.resources == before
