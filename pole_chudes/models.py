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
    # name = models.CharField('Имя игрока', max_length=50)
    score = models.IntegerField('Текущий счет', default=0)
    in_game = models.BooleanField('В игре', default=True)


class Round(models.Model):
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    word_mask = models.CharField('Маска ответа', max_length=20)
    is_complete = models.BooleanField('Завершено', default=False)
    wheel_angle = models.IntegerField('Угол поворота барабана', default=0)
    wheel_sector = models.CharField('Сектор на барабане', max_length=50, null=True, blank=True)
    points_earned = models.IntegerField('Количество выпавших очков', default=0)
    wait_to_spin = models.BooleanField('Вращайте барабан', default=True)
    players = models.ManyToManyField(Player, related_name='rounds', through='RoundPlayer')
    active_player_index = models.IntegerField('Активный игрок', default=0)
    change_at = models.DateTimeField(auto_now=True)
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

    def next_riddle(self):
        self.riddle = Riddle.objects.order_by('?').first()
        self.word_mask = '*' * len(self.riddle.word)
        self.active_player_index = 0
        self.is_complete = False
        self.wait_to_spin = True
        self.comment = None
        while self.players.count() < 3:
            self.add_player()
        for player in self.players.all():
            player.score = 0
            player.in_game = True
            player.save()
        self.save()

    def get_active_player(self) -> Player:
        return self.players.order_by('pk').all()[self.active_player_index]

    def set_active_player(self, in_game=None, score=None, add_score=None):
        player = self.players.order_by('pk').all()[self.active_player_index]
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
        self.comment = f"Игрок {self.active_player_index + 1} победил с результатом {player.score} очков"
        self.is_complete = True

    def next_player(self, comment=None, save=True):
        players = self.players.order_by('pk').all()
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


class RoundPlayer(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
