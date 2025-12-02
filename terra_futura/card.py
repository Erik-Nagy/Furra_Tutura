from __future__ import annotations

from typing import List, Optional
from collections import Counter
from .interfaces import Effect, Resource, InterfaceCard

class Card(InterfaceCard):
    """
    Terra Futura Card implementation.

    Responsibilities:
    - Store resources produced on this card.
    - Track pollution and whether the card is active or inactive.
    - Delegate input/output/pollution validation to its Effect(s).
    - Enforce rules about taking resources from inactive cards.

    UML attributes:
        resources: Resource[]
        pollutionSpacesL: int
        0..1 upperEffect: Effect
        0..1 lowerEffect: Effect
    """

    def __init__(
        self,
        pollutionSpacesL: int = 0,
        upperEffect: Optional[Effect] = None,
        lowerEffect: Optional[Effect] = None,
    ) -> None:
        # resources stored on this card (produced by its effects)
        self.resources: List[Resource] = []

        # how many pollution spaces the card has (top-right icon)
        self.pollutionSpacesL: int = pollutionSpacesL

        # current pollution state
        self._pollution: int = 0   # pollution cubes on safe spaces

        # optional effects
        self.upperEffect: Optional[Effect] = upperEffect
        self.lowerEffect: Optional[Effect] = lowerEffect

    # ------------------------------------------------------------------
    # Pollution logic (Terra Futura rules)
    # ------------------------------------------------------------------

    @property
    def pollution(self) -> int:
        return self._pollution

    @property
    def is_active(self) -> bool:
        """
        Card is active if it has NO pollution cube in the center.
        (Rules: a cube in the center deactivates the card.)
        """
        return self.pollution < self.pollutionSpacesL

    def isActive(self) -> bool:
        return self.is_active

    def canPlacePollution(self, amount: int = 1) -> bool:
        """
        Check if it is legal to place `amount` new pollution cubes
        on this card
        """
        if amount < 0:
            return False
        if not self.is_active:
            return False
        

        free_slots = self.pollutionSpacesL - self._pollution

        if amount > free_slots:
            return False
        
        return True

    def placePollution(self, amount: int = 1) -> None:
        """
        Place `amount` new pollution cubes on this card.
        """

        if amount == 0:
            return

        if not self.canPlacePollution(amount):
            raise ValueError("Cannot place pollution on an inactive card.")

        free_slots = self.pollutionSpacesL - self._pollution
        use_slots = min(free_slots, amount)

        self._pollution += use_slots
        # self.is_active will now reflect center pollution automatically

    # ------------------------------------------------------------------
    # Resource management on this card
    # ------------------------------------------------------------------

    def canPutResources(self, resources: List[Resource]) -> bool:
        """
        Can this card receive these resources as production?
        """
        if not self.is_active:
            return False
        return True

    def putResources(self, resources: List[Resource]) -> None:
        """
        Add resources onto this card
        """
        if not self.canPutResources(resources):
            raise ValueError("Cannot add resources to an inactive card.")
        self.resources.extend(resources)

    def canGetResources(self, resources: List[Resource]) -> bool:
        """
        Can this card give the given resources?
        """
        if not self.is_active:
            return False

        wanted = Counter(resources)
        have = Counter(self.resources)
        # Check wanted multiset is subset of have
        return all(have[r] >= c for r, c in wanted.items())

    def getResources(self, resources: List[Resource]) -> None:
        """
        Remove the given resources from this card.
        """
        if not self.canGetResources(resources):
            raise ValueError("Cannot pay these resources from this card.")

        # Multiset removal
        wanted = Counter(resources)
        new_contents: List[Resource] = []
        current: Counter[Resource] = Counter()

        for r in self.resources:
            # Keep this resource if we have already removed enough of that type
            if current[r] < wanted[r]:
                current[r] += 1
                # skip adding to new_contents -> "removed"
            else:
                new_contents.append(r)

        self.resources = new_contents

    # ------------------------------------------------------------------
    # Effect integration
    # ------------------------------------------------------------------

    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        """
        Validate whether the *upper* effect of this card can be applied with
        the given (input, output, pollution).
        """
        if not self.is_active:
            return False
        if self.upperEffect is None:
            return False

        # Delegate detailed IO check to the effect itself
        return self.upperEffect.check(input, output, pollution)

    def checkLower(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        """
        Same as check(), but for the *lower* effect (usually the bottom
        exchange effect on the card).
        """
        if not self.is_active:
            return False
        if self.lowerEffect is None:
            return False

        return self.lowerEffect.check(input, output, pollution)

    def hasAssistance(self) -> bool:
        """
        True if any of this card's effects involve Assistance.
        """
        upper = self.upperEffect.hasAssistance() if self.upperEffect else False
        lower = self.lowerEffect.hasAssistance() if self.lowerEffect else False
        return upper or lower

    def state(self) -> str:
        """
        Summary, useful for checking whether cards are equal
        """
        status = "active" if self.is_active else "inactive"
        
        statusEffectUpper = self.upperEffect.state() if self.upperEffect else "No effect"
        statusEffectLower = self.lowerEffect.state() if self.lowerEffect else "No effect"
        return (
            f"Card(status={status}, "
            f"upper effect = {statusEffectUpper}, "
            f"lower effect = {statusEffectLower}, "
            f"resources={len(self.resources)}, "
            f"pollution={self._pollution}/{self.pollutionSpacesL}")