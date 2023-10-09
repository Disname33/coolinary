import random

from django.contrib.auth.models import User
from django.db import models


class Riddle(models.Model):
    word = models.CharField('Загаданное слово', max_length=20)
    question = models.CharField('Вопрос', max_length=250)

    def __str__(self):
        return f'{self.question}.[{self.word}]'

    class Meta:
        verbose_name = 'Вопрос для игры'
        verbose_name_plural = 'Вопросы для игры'


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField('Имя игрока', max_length=150, default='Игрок')
    score = models.IntegerField('Текущий счет', default=0)
    in_game = models.BooleanField('В игре', default=True)

    def set(self, user=None, name='Ждун', score=0, in_game=True):
        self.in_game = in_game
        self.score = score
        self.user = user
        self.name = name
        self.save()


class Round(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    word_mask = models.CharField('Маска ответа', max_length=20)
    is_complete = models.BooleanField('Завершено', default=False)
    wheel_angle = models.IntegerField('Угол поворота барабана', default=0)
    wheel_sector = models.CharField('Сектор на барабане', max_length=50, null=True, blank=True)
    points_earned = models.IntegerField('Количество выпавших очков', default=0)
    wait_to_spin = models.BooleanField('Вращайте барабан', default=True)
    players = models.ManyToManyField(Player, related_name='rounds', through='RoundPlayer')
    active_player_index = models.IntegerField('Активный игрок', default=0)
    checked_letters = models.CharField('Проверенные буквы', max_length=32, default='')
    change_at = models.DateTimeField(auto_now=True)
    is_one_device = models.BooleanField('Играть на одном устройстве', default=False)
    comment = models.CharField('Комментарий', max_length=250, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.riddle = Riddle.objects.order_by('?').first()
            self.word_mask = '*' * len(self.riddle.word)
        super(Round, self).save(*args, **kwargs)

    def add_player(self, player=None):
        if self.players.count() < 3:
            if player is None:
                player = Player.objects.create()
            RoundPlayer.objects.create(round=self, player=player)
            return True
        else:
            print("Максимум игроков в комнате")
            return False

    def next_riddle(self, users_id=list, creator=None, is_one_device=False):
        if not users_id:
            users_id = [1]
        while len(users_id) < 3:
            users_id.append(None)
        self.is_one_device = is_one_device
        self.riddle = Riddle.objects.order_by('?').first()
        self.word_mask = '*' * len(self.riddle.word)
        self.active_player_index = 0
        self.is_complete = False
        self.wait_to_spin = True
        self.checked_letters = ''
        self.comment = None
        self.creator = creator
        names = ['Даня', 'Валя', 'Саша', 'Вася', 'Женя']
        while self.players.count() < 3:
            self.add_player()
        players = self.players.order_by('pk').all()[:3]
        for player, user in zip(players, users_id):
            if user > 0:
                _user = User.objects.get(pk=user)
                player.set(user=_user, name=_user.username)
            elif user == 0:
                if is_one_device:
                    player.set(user=players[0].user, name=f'Игрок{player.id}')
                else:
                    player.set(name='Ждун', in_game=False)
            elif user == -1:
                name = random.choice(names)
                names.remove(name)
                player.set(name=name)
            elif user == -2:
                player.set(name='Пусто', in_game=False)
        self.save()

    def get_active_player(self) -> Player:
        return self.players.order_by('pk').all()[self.active_player_index]

    def set_active_player(self, in_game=None, score=None, add_score=None):
        player = self.get_active_player()
        if in_game is not None:
            player.in_game = in_game
        if score is not None:
            player.score = score
        if add_score is not None:
            player.score += add_score
        player.save()

    def win(self):
        player = self.get_active_player()
        self.wait_to_spin = False
        self.comment = f"{player.name} победил(а) с результатом {player.score} очков"
        self.is_complete = True

    def next_player(self, comment=None, save=True):
        players = self.players.order_by('pk').all()[:3]
        self.wait_to_spin = True
        players_count = min(len(players), 3)
        active_player_index = self.active_player_index
        if players_count:
            repeat = 0
            while repeat < players_count:
                repeat += 1
                active_player_index = (active_player_index + 1) % players_count
                if players[active_player_index].in_game:
                    self.active_player_index = active_player_index
                    break
        if comment:
            self.comment = comment
        if save:
            self.save()
        return self.active_player_index

    def is_user_in_game(self, user):
        for player in self.players.order_by('pk').all()[:3]:
            if player.user == user:
                return True
        return False

    def take_vacant_seat(self, user: User):
        for player in self.players.order_by('pk').all()[:3]:
            if player.user is None and player.name == 'Ждун':
                player.set(user=user, name=user.username, in_game=True)
                self.save()
                return player
        return None


class RoundPlayer(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

#
# class SystemMessage(models.Model):
#     round = models.ForeignKey(Round, on_delete=models.CASCADE)
#     comment = models.CharField('Комментарий', max_length=250, null=True, blank=True)
#     action = models.CharField('Действие', max_length=20, null=True, blank=True)
#     player_name = models.CharField('Игрок', max_length=10, null=True, blank=True)
