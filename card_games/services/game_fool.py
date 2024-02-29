from django.contrib.auth.models import User

from ..models import CardPlayer, CardRound, Deck, Card


# class Player:
#     def __init__(self, player_id):
#         self.player_id = player_id
#         self.user = User.objects.get(pk=player_id)
#         self.name = self.user.username
#         self.hand = []
#
#     def add_to_hand(self, cards):
#         self.hand.extend(cards)
#
#     def sort_hand(self):
#         self.hand.sort(key=lambda card: (card.suit.value, card.rank.value))
#
#
# class Table:
#     def __init__(self):
#         self.cards_on_table = []
#
#     def add_cards(self, cards):
#         self.cards_on_table.extend(cards)
#
#     def clear_table(self):
#         self.cards_on_table = []


class GameFool:
    def __init__(self, pk=1, full_deck=False):
        self.game = CardRound.objects.get_or_create(pk=pk)[0]
        self.game.deck = Deck.create_new_deck(52 if full_deck else 36)
        self.game.trump = self.game.deck.cards.last().suit
        players = [
            CardPlayer.objects.get_or_create(user=User.objects.get(id=1))[0],
            CardPlayer.objects.get_or_create(user=User.objects.get(id=3))[0],
            CardPlayer.objects.get_or_create(user=User.objects.get(id=2))[0]
        ]
        self.game.players.set(players)
        self.game.save()

    def start_game(self):
        for player in self.game.players.order_by('pk').all():
            player.hand.set(self.game.deck.deal(6))  # player.hand.add(*self.game.deck.deal(6))
            player.save()
            # player.sort_hand()
        self.game.save()

    # def play_turn(self, player_card):
    #     current_player = self.players[self.current_player_index]
    #     computer_card = self.deck.deal(1)[0]
    #
    #     self.table.add_cards([player_card, computer_card])

    # Реализуйте логику игры, проверку победителя и т.д.

    # self.table.clear_table()
    # self.switch_to_next_player()

    # def next_player(self):
    #     self.game.current_player_index = (self.current_player_index + 1) % len(self.players)

    def attack(self, attacking_card: Card, defending_card: Card):
        return (attacking_card.suit == defending_card.suit and attacking_card.rank > defending_card.rank) \
               or (attacking_card.suit == self.game.deck.trump and defending_card.suit != self.game.deck.trump)
