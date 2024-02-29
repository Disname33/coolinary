from enum import Enum


class Suits(Enum):
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'
    CLUBS = 'Clubs'
    SPADES = 'Spades'
    RED = 'Red'
    BLACK = 'Black'


class Ranks(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    JOKER = 15
