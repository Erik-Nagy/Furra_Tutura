from terra_futura.interfaces import InterfacePile, InterfaceCard
from typing import Optional, List
import random

class Pile(InterfacePile):
    def __init__(self, cards: List[InterfaceCard]) -> None:
        self._discardedCards: List[InterfaceCard] = cards
        self._hiddenCards: List[InterfaceCard] = []

        self._stockHidenCards()
        self._visibleCards: List[InterfaceCard] = self._hiddenCards[-4:]
        self._hiddenCards = self._hiddenCards[:-4]

    def _stockHidenCards(self)-> None:
        random.shuffle(self._discardedCards)
        self._hiddenCards = self._discardedCards
        self._discardedCards = []

    """Only gives the card information, does not change anything"""
    def getCard(self, index:int) ->Optional[InterfaceCard]:
        if 1 <= index <=4:
            return self._visibleCards[index-1]
        
        return None

    """Removes card from pile."""
    def takeCard(self, index: int) -> None:
        if 1 <= index <=4:
            self._visibleCards.pop(index-1)
            if self._hiddenCards:
                self._visibleCards.insert(index-1, self._hiddenCards.pop())            
            if not self._hiddenCards and self._discardedCards:
                self._stockHidenCards()

    def removeLastCard(self) -> None:
        self._discardedCards.append(self._visibleCards.pop(-1))

        if self._hiddenCards:
            self._visibleCards.insert(0, self._hiddenCards.pop())

    def state(self) -> str:
        return (
            f"Number of\n- hidden cards: {len(self._hiddenCards)}\n"
            f"- visible cards: {len(self._visibleCards)}\n"
            f"- discarded cards: {len(self._discardedCards)}"
        )