import pytest
from terra_futura.grid import Grid
from terra_futura.simple_types import GridPosition
from terra_futura.card import Card


def test_put_card() -> None:
    g = Grid()
    origin = GridPosition(0, 0)
    assert g.getCard(origin) is None

    # first card must be on (0, 0)
    assert g.canPutCard(GridPosition(1, 1))
    with pytest.raises(ValueError):
        g.putCard(GridPosition(1, 1), Card())

    # place the first card at (0,0)
    c0 = Card()
    g.putCard(origin, c0)
    assert g.getCard(origin) is c0

    # cannot put on the same position
    assert not g.canPutCard(origin)
    with pytest.raises(ValueError):
        g.putCard(origin, Card())
    # can put only one card
    assert not g.canPutCard(GridPosition(2, 0))
    with pytest.raises(ValueError):
        g.putCard(GridPosition(2, 0), Card())

    # cannot place another card while activation pattern exists
    g2 = Grid()
    g2.putCard(GridPosition(0, 0), Card())
    assert not g2.canPutCard(GridPosition(0, 2))
    with pytest.raises(ValueError):
        g2.putCard(GridPosition(0, 2), Card())


def test_basic_round_activation() -> None:
    g = Grid()
    coord = GridPosition(0, 0)
    g.putCard(coord, Card())

    # test seted activation pattern from putCard
    for y in range(-2, 3):
        assert GridPosition(coord.x, y) in g._canBeActivatedThisTurn
    for x in range(-2, 3):
        assert GridPosition(x, coord.y) in g._canBeActivatedThisTurn

    # canBeActivated initially true
    assert g.canBeActivated(coord)

    # activating marks it as activated this turn
    g.setActivated(coord)
    assert not g.canBeActivated(coord)

    # cannot activate twice in same turn
    with pytest.raises(ValueError):
        g.setActivated(coord)

    # endTurn clears activated
    g.endTurn()
    assert not g.canBeActivated(coord)


def test_last_round_activation() -> None:
    g = Grid()

    # place a 3x3 block of cards
    g._positions = {GridPosition(x, y): Card() for x in (0, 1, 2) for y in (0, 1, 2)}

    # only the main diagonal should be activated
    rel_pattern = [GridPosition(-1, -1), GridPosition(0, 0), GridPosition(1, 1)]

    g.setActivationPattern(rel_pattern)

    # one diagonal card (0,0) should be activatable
    coord = GridPosition(0, 0)
    assert g.canBeActivated(coord)

    # activating it removes it from activationPattern and marks it activated
    g.setActivated(coord)
    assert coord in g._activatedThisTurn
    assert coord not in g._activationPattern
    assert not g.canBeActivated(coord)
