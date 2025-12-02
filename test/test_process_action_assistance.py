import pytest

from typing import List, Optional, Dict
from terra_futura.simple_types import Resource
from terra_futura.simple_types import GridPosition
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.card import Card
from terra_futura.interfaces import InterfaceGrid, InterfaceCard, Effect
from terra_futura.transformation_fixed import TransformationFixed
from collections import Counter

class DummyGrid(InterfaceGrid):
    def __init__(self, mapping: Dict[GridPosition, InterfaceCard]) -> None:
        self.mapping: Dict[GridPosition, InterfaceCard] = mapping

    def getCard(self, position: GridPosition) -> Optional[InterfaceCard]:
        return self.mapping.get(position)
    
    def canPutCard(self, coordinate: GridPosition)-> bool:
        return True

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> bool:
        return True

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
    
class AlwaysAssistanceEffect(Effect):
    def hasAssistance(self) -> bool:
        return True
    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return True
    def state(self) -> str:
        return 'AlwaysAssistEffect'
    

class TransformationFixedAlwaysAssist(TransformationFixed):
    def hasAssistance(self) -> bool:
        return True
    


class DummyPlayer:
    """
    Minimal dummy player wrapper for supplying a grid.
    """

    def __init__(self, grid: DummyGrid) -> None:
        self._grid = grid

    def getGrid(self) -> DummyGrid:
        return self._grid


def test_good_scenario_no_outputs() -> None:
    logic = ProcessActionAssistance()

    
    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED, Resource.GREEN])
    main_grid = DummyGrid({GridPosition(1,1): main_card})
    main_pos = GridPosition(1,1)

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main_pos), (Resource.RED, main_pos)]
    outputs: List[tuple[Resource, GridPosition]] = []
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )

    assert result is True
    assert len(main_card.resources) == 0

def test_good_scenario_outputs() -> None:
    logic = ProcessActionAssistance()

    
    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED, Resource.GREEN])
    main_grid = DummyGrid({GridPosition(1,1): main_card})
    main_pos = GridPosition(1,1)

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is True
    assert main_card.resources == [Resource.FOOD]

def test_outputs_not_in_same_location() -> None:
    logic = ProcessActionAssistance()

    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED, Resource.GREEN])
    main_grid = DummyGrid({GridPosition(1,1): main_card})
    main_pos = GridPosition(1,1)

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, GridPosition(-1,0)), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is False
    assert Counter(main_card.resources) == Counter([Resource.GREEN, Resource.RED])

def test_resources_not_in_same_location() -> None:
    logic = ProcessActionAssistance()

    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED])
    main_pos = GridPosition(1,1)
    main2_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main2_pos = GridPosition(-1,0)
    main2_card.putResources([Resource.GREEN])
    main_grid = DummyGrid({main_pos: main_card, main2_pos:main2_card})
    

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main2_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is True
    assert Counter(main_card.resources) == Counter([Resource.FOOD])

def test_missing_resources() -> None:
    logic = ProcessActionAssistance()

    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED])
    main_pos = GridPosition(1,1)
    main2_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main2_pos = GridPosition(-1,0)
    main_grid = DummyGrid({main_pos: main_card, main2_pos:main2_card})
    

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main2_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is False
    assert Counter(main_card.resources) == Counter([Resource.RED])
    

def test_inactive_card() -> None:
    logic = ProcessActionAssistance()

    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED])
    main_pos = GridPosition(1,1)
    main2_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main2_card.putResources([Resource.GREEN])
    main2_card.placePollution(1)
    main2_pos = GridPosition(-1,0)
    main_grid = DummyGrid({main_pos: main_card, main2_pos:main2_card})
    

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 0))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main2_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution: List[GridPosition] = []

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is False
    assert Counter(main_card.resources) == Counter([Resource.RED])
    assert Counter(main2_card.resources) == Counter([Resource.GREEN])
    

def test_create_pollution_on_main_card() -> None:
    logic = ProcessActionAssistance()

    
    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED, Resource.GREEN])
    main_grid = DummyGrid({GridPosition(1,1): main_card})
    main_pos = GridPosition(1,1)

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 1))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution = [main_pos]

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is True
    assert main_card.resources == [Resource.FOOD]
    assert main_card.pollution == 1

def test_create_pollution_on_missing_card() -> None:
    logic = ProcessActionAssistance()
    
    main_card = Card(pollutionSpacesL=1, upperEffect=AlwaysAssistanceEffect())
    main_card.putResources([Resource.RED, Resource.GREEN])
    main_grid = DummyGrid({GridPosition(1,1): main_card})
    main_pos = GridPosition(1,1)

    other_card = Card(pollutionSpacesL=1, upperEffect=TransformationFixedAlwaysAssist([Resource.GREEN, Resource.RED], [Resource.FOOD], 1))
    other_grid = DummyGrid({GridPosition(0,1): other_card})
    

    assistingPlayer = DummyPlayer(other_grid)
    inputs = [(Resource.GREEN, main_pos), (Resource.RED, main_pos)]
    outputs = [(Resource.FOOD, main_pos)]
    pollution = [GridPosition(-1, 1)]

    result = logic.activateCard(
        main_card, main_grid,
        assistingPlayer, other_card,
        inputs, outputs, pollution
    )
    assert result is False
    assert Counter(main_card.resources) == Counter([Resource.RED, Resource.GREEN])
