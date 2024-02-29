from django.contrib.auth.models import User
from django.db import models

from .fields import ModelIdArrayField


class Card(models.Model):
    class Suits(models.IntegerChoices):
        HEARTS = 1, 'Hearts'
        DIAMONDS = 2, 'Diamonds'
        CLUBS = 3, 'Clubs'
        SPADES = 4, 'Spades'
        RED = 5, 'Red'
        BLACK = 6, 'Black'

    class Ranks(models.IntegerChoices):
        TWO = 2, '2'
        THREE = 3, '3'
        FOUR = 4, '4'
        FIVE = 5, '5'
        SIX = 6, '6'
        SEVEN = 7, '7'
        EIGHT = 8, '8'
        NINE = 9, '9'
        TEN = 10, '10'
        JACK = 11, 'Jack'
        QUEEN = 12, 'Queen'
        KING = 13, 'King'
        ACE = 14, 'Ace'
        JOKER = 15, 'Joker'

    suit = models.IntegerField(choices=Suits.choices)
    rank = models.IntegerField(choices=Ranks.choices)

    def serialize(self):
        return ((self.suit & 0x3F) << 6) | (self.rank & 0x3F)

    @classmethod
    def deserialize(cls, serialized_data):
        return cls((serialized_data >> 6) & 0x3F, serialized_data & 0x3F)

    def __str__(self):
        return f"{self.get_suit_display()} {self.get_rank_display().upper()}"

    class Meta:
        verbose_name = 'Игральные карты'

    @classmethod
    def create_deck(cls):
        suits = list(Card.Suits)[:4]
        ranks = list(Card.Ranks)[:13]
        deck = [Card.objects.create(suit=suit.value, rank=rank.value) for suit in suits for rank in ranks]
        deck.append(Card.objects.create(suit=Card.Suits.RED.value, rank=Card.Ranks.JOKER.value))
        deck.append(Card.objects.create(suit=Card.Suits.BLACK.value, rank=Card.Ranks.JOKER.value))
        for card in deck:
            card.save()

        return deck


class Deck(models.Model):
    # cards = models.ManyToManyField(Card, related_name='%(class)s_cards')
    cards = ModelIdArrayField(model_class=Card, max_length=200, default=list)

    @classmethod
    def create_new_deck(cls, number=54):
        suits_range = list(range(Card.Suits.HEARTS.value, Card.Suits.SPADES.value + 1))
        ranks_range = list(range(Card.Ranks.SIX.value, Card.Ranks.ACE.value + 1))

        if number == 54:
            deck = Card.objects.all().order_by('?')
        elif number == 52:
            deck = Card.objects.filter(suit__in=suits_range).order_by('?')
        else:  # if number == 36:
            deck = Card.objects.filter(suit__in=suits_range, rank__in=ranks_range).order_by('?')

        new_deck = Deck.objects.create()
        new_deck.cards = deck

        return new_deck

    class Meta:
        verbose_name = 'Колода'
        verbose_name_plural = 'Колоды'

    #
    # def deal(self, num_cards):
    #     if num_cards > self.cards.count():
    #         num_cards = self.cards.count()
    #     dealt_cards = self.cards.all()[:num_cards]
    #     self.cards.set(self.cards.all()[num_cards:])
    #     self.save()
    #     return dealt_cards

    def deal(self, num_cards):
        cards_in_deck = self.cards
        if num_cards > len(cards_in_deck):
            num_cards = len(cards_in_deck)
        dealt_cards = cards_in_deck[:num_cards]
        self.cards = cards_in_deck[num_cards:]
        self.save()
        return dealt_cards


class Table(models.Model):
    attacking_cards = models.ManyToManyField(Card, related_name='%(class)s_attacking_cards')
    defending_cards = models.ManyToManyField(Card, related_name='%(class)s_defending_cards')

    class Meta:
        verbose_name = 'Карты на столе'


class CardPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    hand = models.ManyToManyField(Card, related_name='players_hands')
    in_game = models.BooleanField('В игре', default=True)

    def __str__(self):
        if self.user is None:
            return 'пусто'
        return self.user.username

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class CardRound(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, null=True, blank=True)
    # deck = ModelIdArrayField(model_class=Card, max_length=200)
    trump = models.IntegerField('Козырь', choices=Card.Suits.choices, null=True, blank=True)
    # table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
    is_complete = models.BooleanField('Завершено', default=False)
    game = models.IntegerField('Игра', default=0)
    parameters = models.IntegerField('Параметры', default=0)
    bet = models.IntegerField('Ставка', default=100)
    players_count = models.IntegerField('Количество игроков', default=2)
    players = models.ManyToManyField(CardPlayer, related_name='rounds', through='RoundPlayer')
    attacking_player_index = models.IntegerField('Атакующий игрок', default=1)
    defending_player_index = models.IntegerField('Защищающийся игрок', default=2)
    change_at = models.DateTimeField(auto_now=True)
    comment = models.CharField('Комментарий', max_length=250, null=True, blank=True)

    #
    #     def save(self, *args, **kwargs):
    #         if not self.pk:
    #             self.riddle = Riddle.objects.order_by('?').first()
    #             self.word_mask = '*' * len(self.riddle.word)
    #         super(Round, self).save(*args, **kwargs)
    #
    #     def add_player(self, player=None):
    #         if self.players.count() < 3:
    #             if player is None:
    #                 player = Player.objects.create()
    #             RoundPlayer.objects.create(round=self, player=player)
    #             return True
    #         else:
    #             print("Максимум игроков в комнате")
    #             return False
    #
    #     def new_round(self, users_id=list, creator=None, is_one_device=False):
    #         if not users_id:
    #             users_id = [1]
    #         while len(users_id) < 3:
    #             users_id.append(None)
    #         self.is_one_device = is_one_device
    #         self.riddle = Riddle.objects.order_by('?').first()
    #         self.word_mask = '*' * len(self.riddle.word)
    #         self.active_player_index = 0
    #         self.is_complete = False
    #         self.wait_to_spin = True
    #         self.checked_letters = ''
    #         self.comment = None
    #         self.creator = creator
    #         names = ['Даня', 'Валя', 'Саша', 'Вася', 'Женя']
    #         while self.players.count() < 3:
    #             self.add_player()
    #         players = self.players.order_by('pk').all()[:3]
    #         for player, user in zip(players, users_id):
    #             if user > 0:
    #                 _user = User.objects.get(pk=user)
    #                 player.set(user=_user, name=_user.username)
    #             elif user == 0:
    #                 if is_one_device:
    #                     player.set(user=players[0].user, name=f'Игрок{player.id}')
    #                 else:
    #                     player.set(name='Ждун', in_game=False)
    #             elif user == -1:
    #                 name = random.choice(names)
    #                 names.remove(name)
    #                 player.set(name=name)
    #             elif user == -2:
    #                 player.set(name='Пусто', in_game=False)
    #         self.save()
    #
    #     def get_active_player(self) -> Player:
    #         return self.players.order_by('pk').all()[self.active_player_index]
    #
    #     def set_active_player(self, in_game=None, score=None, add_score=None):
    #         player = self.get_active_player()
    #         if in_game is not None:
    #             player.in_game = in_game
    #         if score is not None:
    #             player.score = score
    #         if add_score is not None:
    #             player.score += add_score
    #         player.save()
    #
    #     def win(self):
    #         player = self.get_active_player()
    #         self.wait_to_spin = False
    #         self.comment = f"{player.name} победил(а) с результатом {player.score} очков"
    #         self.is_complete = True
    #
    #     def next_player(self, comment=None, save=True):
    #         players = self.players.order_by('pk').all()[:3]
    #         self.wait_to_spin = True
    #         players_count = min(len(players), 3)
    #         active_player_index = self.active_player_index
    #         if players_count:
    #             repeat = 0
    #             while repeat < players_count:
    #                 repeat += 1
    #                 active_player_index = (active_player_index + 1) % players_count
    #                 if players[active_player_index].in_game:
    #                     self.active_player_index = active_player_index
    #                     break
    #         if comment:
    #             self.comment = comment
    #         if save:
    #             self.save()
    #         return self.active_player_index
    #
    #     def is_user_in_game(self, user):
    #         for player in self.players.order_by('pk').all()[:3]:
    #             if player.user == user:
    #                 return True
    #         return False

    def take_vacant_seat(self, user: User):
        if self.players.count() < self.players_count:
            player = CardPlayer.objects.get_or_create(user=user)[0]
            self.players.get_or_create(player)
            self.save()
            return True
        return False


class RoundPlayer(models.Model):
    round = models.ForeignKey(CardRound, on_delete=models.CASCADE)
    player = models.ForeignKey(CardPlayer, on_delete=models.CASCADE)
