from typing import List, Tuple, Any, Optional
import unittest
import json
from terra_futura.activation_pattern import ActivationPattern
from terra_futura.interfaces import InterfaceGrid, InterfaceCard 
from terra_futura.simple_types import GridPosition 
class GridFake(InterfaceGrid):
    activations_received: List[GridPosition] 
    
    def __init__(self) -> None:
        self.activations_received = []

    def setActivationPattern(self, pattern: List[GridPosition]) -> None:
        self.activations_received = pattern

    def putCard(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        pass
    
# Has to return something
    def getCard(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        return None 
    
    def canPutCard(self, coordinate: GridPosition) -> bool:
        return True 
        
    def canBeActivated(self, coordinate: GridPosition) -> bool:
        return False
        
    def setActivated(self, coordinate: GridPosition) -> None:
        ...
        
    def endTurn(self) -> None:
        ...

    def state(self) -> str:
        return ""

def create_grid_positions_from_tuples(tuples: List[Tuple[int, int]]) -> List[GridPosition]:
    """Converts the test tuple patterns into the required GridPosition objects."""
    return [GridPosition(x, y) for x, y in tuples]


# Unit Tests
class TestActivationPattern(unittest.TestCase):
    def setUp(self) -> None:
        self.grid_fake: GridFake = GridFake()
        
        raw_tuples: List[Tuple[int, int]] = [(0, 0), (-1, 1), (0, 0)]
        
        initial_pattern: List[GridPosition] = create_grid_positions_from_tuples(raw_tuples)
        
        self.activation_pattern = ActivationPattern(
            self.grid_fake, initial_pattern)

    def check_state(self, activations: List[Tuple[int, int]], is_selected: bool) -> None:
        state: Any = json.loads(self.activation_pattern.state())
        self.assertEqual(state["selected"], is_selected)
        self.assertCountEqual(state["activations"], [
                              list(x) for x in activations])

    def test_activation_pattern_forwards_its_data_when_selected(self) -> None:
        test_pattern_tuples: List[Tuple[int, int]] = [(0, 0), (0, 0), (-1, 1)]
        expected_output: List[GridPosition] = create_grid_positions_from_tuples(test_pattern_tuples)
        
        self.check_state(test_pattern_tuples, False)
        self.activation_pattern.select()
        self.check_state(test_pattern_tuples, True)
        
        self.assertCountEqual(self.grid_fake.activations_received, expected_output)

    def test_pattern_cannot_be_activated_twice(self) -> None:
        self.activation_pattern.select()
        with self.assertRaises(AssertionError):
            self.activation_pattern.select()

if __name__ == "__main__":
    unittest.main()