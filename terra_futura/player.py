from dataclasses import dataclass
from .activation_pattern import ActivationPattern
from .scoring_method import ScoringMethod
from .grid import Grid
from .interfaces import PlayerInterface, InterfaceGrid


@dataclass
class Player(PlayerInterface):
    id: int
    activation_patterns: list[ActivationPattern]
    scoring_methods: list[ScoringMethod]
    grid: InterfaceGrid
    hasBeenAssisted: bool = False
    
    def __post_init__(self) -> None:
        if len(self.activation_patterns) != 2:
            raise Exception("Incorrect number of activation patterns")
        if len(self.scoring_methods) != 2:
            raise Exception("Incorrect number of scoring methods")
        
    def getGrid(self) -> InterfaceGrid:
        return self.grid
    
    def getId(self) -> int:
        return self.id
