import pytest
from terra_futura.grid import Grid
from terra_futura.simple_types import GridPosition
from terra_futura.card import Card


def testPutCardAndGridProperties() -> None:
    g = Grid()
    origin = GridPosition(0, 0)
    assert g.getCard(origin) is None

    # first card must be on (0, 0)
    assert g.canPutCard(GridPosition(1, 1))
    with pytest.raises(ValueError):
        g.putCard(GridPosition(1, 1), Card())

    #place the first card at (0,0)
    c0 = Card()
    g.putCard(origin, c0)
    assert g.getCard(origin) is c0
    g.endTurn()

    # cannot put on the same position
    assert not g.canPutCard(origin)
    with pytest.raises(ValueError):
        g.putCard(origin, Card())

    # test width limit
    assert g.canPutCard(GridPosition(2, 0))
    g.putCard(GridPosition(2, 0), Card())
    g.endTurn()
    with pytest.raises(ValueError):
        g.canPutCard(GridPosition(3, 0))
    assert not g.canPutCard(GridPosition(-1, 0))

    # test height limit
    g2 = Grid()
    g2.putCard(GridPosition(0, 0), Card())
    g2.endTurn()
    g2.putCard(GridPosition(0, 2), Card())
    g2.endTurn()
    with pytest.raises(ValueError):
        g2.canPutCard(GridPosition(0, 3))
    with pytest.raises(ValueError):
        g2.putCard(GridPosition(0, 3), Card())
    assert not g2.canPutCard(GridPosition(0,-1))


def testWhichCardsShouldActivateOneCard() -> None:
    g = Grid()
    coord = GridPosition(0, 0)
    g.putCard(coord, Card())

    # test seted activation pattern from putCard
    assert {coord} == g.shouldBeActivated

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
    assert not g.canBeActivated(coord)

def testTriedPuttingMoreCardsInOneTurn() -> None:
    g = Grid()
    coord = GridPosition(0, 0)
    g.putCard(coord, Card())
    assert not g.canPutCard(GridPosition(1,0))
    g.endTurn()
    assert g.canPutCard(GridPosition(1,0))

def testWhichCardsShouldActivateMultipleCards() -> None:
    g = Grid()
    coord = GridPosition(0, 0)
    g.putCard(coord, Card())

    assert {coord} == g.shouldBeActivated
    g.endTurn()

    g.putCard(GridPosition(1,0), Card())

    assert {coord, GridPosition(1,0)} == g.shouldBeActivated

    g.endTurn()

    g.putCard(GridPosition(1,1), Card())

    assert {GridPosition(1,1), GridPosition(1,0)} == g.shouldBeActivated

    g.endTurn()

    g.putCard(GridPosition(2,2), Card())

    assert {GridPosition(2,2)} == g.shouldBeActivated

    g.endTurn()

    g.putCard(GridPosition(2,0), Card())

    assert {GridPosition(2,2), coord, GridPosition(1,0), GridPosition(2,0)} == g.shouldBeActivated