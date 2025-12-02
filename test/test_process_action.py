import pytest

from terra_futura.process_action import ProcessAction
from terra_futura.card import Card
from terra_futura.arbitrary_basic import ArbitraryBasic
from terra_futura.simple_types import Resource, GridPosition
from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from typing import Optional, List

class DummyGrid(InterfaceGrid):
    def __init__(self, mapping: dict[GridPosition, InterfaceCard]) -> None:
        self.mapping = mapping

    def getCard(self, position: GridPosition) -> Optional[InterfaceCard]:
        return self.mapping.get(position)
    
    def canPutCard(self, coordinate: GridPosition)-> bool:
        return True

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        pass

    def canBeActivated(self, coordinate: GridPosition)-> bool:
        return True
        
    def setActivated(self, coordinate: GridPosition) -> None:
        pass

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        pass
        
    def endTurn(self) -> None:
        pass

    def state(self) -> str:
        return ""


def test_activate_card_inactive_returns_false() -> None:
    pa = ProcessAction()
    # create an inactive card (no safe pollution slots) and ensure activation is rejected
    card = Card(pollutionSpacesL=0)
    grid = DummyGrid({})

    result = pa.activateCard(card, grid, inputs=[], outputs=[], pollution=[])
    assert result is False


def test_activate_card_rejects_when_pollution_cannot_be_placed() -> None:
    pa = ProcessAction()
    # acting card is active
    acting = Card()
    # target card has 0 safe slots, trying to place 2 would require center cubes -> rejected
    target = Card(pollutionSpacesL=0)
    pos = GridPosition(0, 0)
    grid = DummyGrid({pos: target})

    result = pa.activateCard(acting, grid, inputs=[], outputs=[], pollution=[pos, pos])
    assert result is False
    # ensure no pollution was placed (target remains inactive / unchanged)
    # don't rely on internal attribute names for center slots; just assert activation failed
    

def test_activate_card_rejects_when_inputs_not_available() -> None:
    pa = ProcessAction()
    acting = Card()
    # resource provider at P has no resources
    resource_card = Card()
    pos = GridPosition(1, 0)
    grid = DummyGrid({pos: resource_card})

    result = pa.activateCard(acting, grid, inputs=[(Resource.YELLOW, pos)], outputs=[], pollution=[])
    assert result is False


def test_activate_card_rejects_when_outputs_cannot_be_put() -> None:
    pa = ProcessAction()
    # make acting card unable to accept outputs by creating it inactive
    acting = Card(pollutionSpacesL=0)
    pos = GridPosition(1, 1)
    grid = DummyGrid({pos: acting})

    result = pa.activateCard(acting, grid, inputs=[], outputs=[(Resource.GOODS, pos)], pollution=[])
    assert result is False
    
def test_activate_card_rejects_when_output_targets_different_active_card() -> None:
    pa = ProcessAction()
    acting = Card()
    # another active card at a different position -- outputs must target the acting card
    other = Card()
    pos_act = GridPosition(0, 0)
    pos_other = GridPosition(1, 0)
    grid = DummyGrid({pos_act: acting, pos_other: other})

    result = pa.activateCard(acting, grid, inputs=[], outputs=[(Resource.GOODS, pos_other)], pollution=[])
    assert result is False


def test_activate_card_success_performs_actions() -> None:
    pa = ProcessAction()
    # acting card has two resources to pay and an effect that requires 2 inputs,
    # produces pollution and fills safe slots as available
    acting = Card(pollutionSpacesL=2, upperEffect=ArbitraryBasic(from_=2, to=[Resource.MONEY], pollution=2))
    # give acting card the resources it will pay
    acting.resources = [Resource.YELLOW, Resource.RED]

    # place pollution on a different card so the acting card does not
    # become inactive before its inputs are collected
    target = Card(pollutionSpacesL=2)
    pos_act = GridPosition(0, 0)
    pos_target = GridPosition(1, 1)
    grid = DummyGrid({pos_act: acting, pos_target: target})

    inputs = [(Resource.YELLOW, pos_act), (Resource.RED, pos_act)]
    outputs = [(Resource.MONEY, pos_act)]
    pollution = [pos_target, pos_target]

    result = pa.activateCard(acting, grid, inputs=inputs, outputs=outputs, pollution=pollution)

    assert result is True

    # verify resources: inputs removed, output added
    assert acting.resources == [Resource.MONEY]