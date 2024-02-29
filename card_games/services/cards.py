import random

from .enums import Ranks, Suits


class Card:
    def __init__(self, suit: Suits, rank: Ranks):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        rank = self.rank.name if self.rank.value > 10 else self.rank.value
        return f"{self.suit.name.capitalize()} {rank}"

    def __int__(self):
        return self.suit.value * 100 + self.rank.value

    def get_id(self):
        return int(self)

    @staticmethod
    def create_by_id(card_id: int):
        suit = Suits(card_id // 100)
        rank = Ranks(card_id % 100)
        return Card(suit, rank)


class Deck:
    def __init__(self, cards_in_deck=54):
        self.suits = list(Suits)[:4]
        self.ranks = list(Ranks)[:13] if cards_in_deck != 36 else list(Ranks)[4:13]
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        if cards_in_deck == 54:
            self.cards.append(Card(Suits.RED, Ranks.JOKER))
            self.cards.append(Card(Suits.BLACK, Ranks.JOKER))
        self.shuffle()
        self.last = self.cards[-1]
        self.trump = self.last.suit

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        if num_cards > len(self.cards):
            num_cards = len(self.cards)
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards
