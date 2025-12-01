import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from terra_futura.simple_types import Resource, GridPosition
from terra_futura.card import Card
from terra_futura.interfaces import InterfaceGrid, InterfaceCard
from terra_futura.select_reward import SelectReward
from typing import Optional, List
from terra_futura.transformation_fixed import TransformationFixed


class DummyGrid (InterfaceGrid):
    def __init__(self) ->None:
        self.grid: dict[GridPosition, InterfaceCard] = {}
    
    def getCard(self, coordinate: GridPosition)-> Optional[InterfaceCard]:
        return self.grid.get(coordinate)

    def canPutCard(self, coordinate: GridPosition)-> bool:
        if self.getCard(coordinate) == None:
            return True
        return False

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> bool:
        if self.canPutCard(coordinate):
            self.grid[coordinate] = card
            return True
        return False

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
    

class DummyPlayer:

    def __init__(self, grid: DummyGrid) -> None:
        self.id = 0
        self._grid = grid

    def getGrid(self) -> DummyGrid:
        return self._grid
    

class TestScoringMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.selectReward = SelectReward

    def test_selectRewardNotYetSet(self) ->None:
        player = DummyPlayer(DummyGrid())
        selection = self.selectReward()
        self.assertEqual("Reward has not been set",  selection.state())
    
    def test_selectRewardNotYetSetButTriedToSelect(self) ->None:
        player = DummyPlayer(DummyGrid())
        card = Card(pollutionSpacesL=2)
        selection = self.selectReward()
        selection.selectReward(Resource.RED)
        self.assertEqual(False, card.canGetResources([Resource.RED]))
        self.assertEqual("Reward has not been set",  selection.state())

    def test_selectRewardSetButCardNotOnPlayerGrid(self) ->None:
        player = DummyPlayer(DummyGrid())
        card = Card(pollutionSpacesL=2)
        selection = self.selectReward()
        selection.setReward(player, card, [Resource.RED, Resource.GREEN])
        selection.selectReward(Resource.RED)
        self.assertEqual(False, card.canGetResources([Resource.RED]))
        self.assertEqual("Reward has not been set",  selection.state())

    def test_selectRewardSetButCardWasPutOnWrongPosition(self) ->None:
        player = DummyPlayer(DummyGrid())
        card = Card(pollutionSpacesL=2)
        with self.assertRaises(ValueError):
            player.getGrid().putCard(GridPosition(20,0), card)
        selection = self.selectReward()
        selection.setReward(player, card, [Resource.RED, Resource.GREEN])
        selection.selectReward(Resource.RED)
        self.assertEqual(False, card.canGetResources([Resource.RED]))
        self.assertEqual("Reward has not been set",  selection.state())

    def test_selectRewardSetAndSelectedCorrectly(self) ->None:
        player = DummyPlayer(DummyGrid())
        card = Card(pollutionSpacesL=2)
        player.getGrid().putCard(GridPosition(0,0), card)
        selection = self.selectReward()
        selection.setReward(player, card, [Resource.RED, Resource.GREEN])
        selection.selectReward(Resource.RED)
        self.assertEqual(True, card.canGetResources([Resource.RED]))
        self.assertEqual("Player number 0 is picking from [<Resource.RED: 2>, <Resource.GREEN: 3>]",  selection.state())

    def test_selectRewardSetWrongCard(self) ->None:
        player = DummyPlayer(DummyGrid())
        card1 = Card(pollutionSpacesL=2, upperEffect= TransformationFixed([Resource.RED, Resource.GREEN], [Resource.GOODS, Resource.YELLOW], 0))
        card2 = Card(pollutionSpacesL=2, upperEffect= TransformationFixed([Resource.RED, Resource.YELLOW], [Resource.GOODS, Resource.YELLOW], 0))
        player.getGrid().putCard(GridPosition(0,0), card1)
        selection = self.selectReward()
        selection.setReward(player, card2, [Resource.RED, Resource.GREEN])
        selection.selectReward(Resource.RED)
        self.assertEqual(False, card1.canGetResources([Resource.RED]))
        self.assertEqual("Reward has not been set",  selection.state())

    def test_selectRewardSetAndSelectedCorrectly2(self) ->None:
        player = DummyPlayer(DummyGrid())
        card1 = Card(pollutionSpacesL=2, upperEffect= TransformationFixed([Resource.RED, Resource.GREEN], [Resource.GOODS, Resource.YELLOW], 0), lowerEffect = TransformationFixed([Resource.RED, Resource.YELLOW], [Resource.GOODS, Resource.YELLOW], 0))
        card2 = Card(pollutionSpacesL=2, upperEffect= TransformationFixed([Resource.RED, Resource.GREEN], [Resource.GOODS, Resource.YELLOW], 0), lowerEffect = TransformationFixed([Resource.RED, Resource.RED], [Resource.GOODS, Resource.YELLOW], 0))
        card3 = Card(pollutionSpacesL=1, upperEffect= TransformationFixed([Resource.RED, Resource.GREEN], [Resource.GOODS, Resource.YELLOW], 0), lowerEffect = TransformationFixed([Resource.RED, Resource.YELLOW], [Resource.GOODS, Resource.YELLOW], 0))
        player.getGrid().putCard(GridPosition(0,0), card1)

        self.assertEqual(False, player.getGrid().putCard(GridPosition(0,0), card2))
        self.assertEqual(card1, player.getGrid().getCard(GridPosition(0,0)))

        player.getGrid().putCard(GridPosition(1,0), card2)
        player.getGrid().putCard(GridPosition(2,0), card3)

        selection = self.selectReward()
        selection.setReward(player, card1, [Resource.RED, Resource.GREEN])
        selection.selectReward(Resource.RED)
        self.assertEqual(True, card1.canGetResources([Resource.RED]))
        self.assertEqual(False, card2.canGetResources([Resource.RED]))
        self.assertEqual(False, card3.canGetResources([Resource.RED]))
        self.assertEqual("Player number 0 is picking from [<Resource.RED: 2>, <Resource.GREEN: 3>]",  selection.state())
