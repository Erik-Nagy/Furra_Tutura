from dataclasses import dataclass
from .activation_pattern import ActivationPattern
from .scoring_method import ScoringMethod
from .grid import Grid
from .interfaces import PlayerInterface

@dataclass
class Player(PlayerInterface):
    id: int
    activation_patterns: list[ActivationPattern]
    scoring_methods: list[ScoringMethod]
    grid: Grid
    hasBeenAssisted: bool = False
    
    def __post_init__(self) -> None:
        if len(self.activation_patterns) != 2:
            raise Exception("Incorrect number of activation patterns")
        if len(self.scoring_methods) != 2:
            raise Exception("Incorrect number of scoring methods")
        
    def getGrid(self) -> Grid:
        return self.grid
    
    def getId(self) -> int:
        return self.id
