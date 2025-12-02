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

    # test width limit
    assert g.canPutCard(GridPosition(2, 0))
    g.putCard(GridPosition(2, 0), Card())
    assert not g.canPutCard(GridPosition(3, 0))

    # test height limit
    g2 = Grid()
    g2.putCard(GridPosition(0, 0), Card())
    g2.putCard(GridPosition(0, 2), Card())
    assert not g2.canPutCard(GridPosition(0, 3))
    with pytest.raises(ValueError):
        g2.putCard(GridPosition(0, 3), Card())


def test_activation_pattern_and_can_be_activated_and_set_activated() -> None:
    g = Grid()
    coord = GridPosition(1, 1)
    g.putCard(coord, Card())

    # test seted activation pattern from putCard
    for y in range(-2, 3):
        assert GridPosition(coord.x, y) in g._activationPattern
    for x in range(-2, 3):
        assert GridPosition(x, coord.y) in g._activationPattern

    # canBeActivated initially true
    assert g.canBeActivated(coord)

    # activating marks it as activated this turn
    g.setActivated(coord)
    assert not g.canBeActivated(coord)

    # cannot activate twice in same turn
    with pytest.raises(ValueError):
        g.setActivated(coord)

    # endTurn clears activated set
    g.endTurn()
    assert g.canBeActivated(coord)
