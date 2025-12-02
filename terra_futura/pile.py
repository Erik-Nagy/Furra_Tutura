from abc import ABC, abstractmethod
from .interfaces import InterfaceCard, InterfacePile
import random
import time
from typing import Optional, List
from collections.abc import Sequence

class InterfaceShuffler(ABC):
    @abstractmethod
    def shuffle(self, deck: list[InterfaceCard]) -> list[InterfaceCard]:
        pass


class RandomShuffler(InterfaceShuffler):
    def __init__(self) -> None:
        seed = int(time.time())
        self.rng = random.Random(seed)
    
    def shuffle(self, deck: list[InterfaceCard]) -> list[InterfaceCard]:
        deck_copy = deck.copy()
        self.rng.shuffle(deck_copy)
        return deck_copy

class Pile(InterfacePile):
    def __init__(self, visible_cards: Sequence[InterfaceCard], hidden_cards: Sequence[InterfaceCard], shuffler: Optional['InterfaceShuffler'] = None):
        if not shuffler:
            shuffler = RandomShuffler()
        self.shuffler = shuffler
        self.visible_cards: List[InterfaceCard] = list(visible_cards)
        if len(self.visible_cards) != 4:
            raise ValueError("Not 4 visible cards")
        self.hidden_cards: List[InterfaceCard] = list(hidden_cards)
        self.discarded_cards: List[InterfaceCard] = []
          
    def getCard(self, index: int) -> Optional[InterfaceCard]:
        if index < 1 or index > 4:
            return None
        
        return self.visible_cards[index-1]
    
    def takeCard(self, index: int) -> InterfaceCard:
        if index < 1 or index > 5:
            raise ValueError("Cannot get card at that position")
        
        if self.hidden_cards == []:
            self.hidden_cards = self.shuffler.shuffle(self.discarded_cards)
            self.discarded_cards.clear()

            if self.hidden_cards == []:
                raise ValueError("Empty pile")
        topDeck = self.hidden_cards.pop()
        
        if index == 5:
            return topDeck
        
        card = self.visible_cards.pop(index-1)
        self.visible_cards.insert(0, topDeck)
        return card
    
    def removeLastCard(self) -> None:
        if self.hidden_cards == []:
            self.hidden_cards = self.shuffler.shuffle(self.discarded_cards)
            self.discarded_cards.clear()

            if self.hidden_cards == []:
                raise ValueError("Empty pile")
        topDeck = self.hidden_cards.pop()

        self.discarded_cards.append(self.visible_cards.pop())
        self.visible_cards.insert(0, topDeck)

    def state(self) -> str:
        out = ''
        
        for i,x in enumerate(self.visible_cards):
            out += f'Visible {i}: {x.state()}\n'
        for i,x in enumerate(self.hidden_cards):
            out += f'Hidden {i}: {x.state()}\n'
        for i,x in enumerate(self.discarded_cards):
            out += f'Discarded {i}: {x.state()}\n'
        
        return out