from django.contrib.auth.models import User
from django.db import models


class TetrisScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField('Счёт')
    lines = models.IntegerField('Линии')
    level = models.IntegerField('Уровень')
    date = models.DateTimeField(auto_now=True, blank=True, verbose_name='Дата')

    @classmethod
    def create(cls, request):
        return cls(
            user=request.user,
            score=request.GET.get('score'),
            lines=request.GET.get('lines'),
            level=request.GET.get('level')
        )

    def __str__(self):
        return f'Игрок: {self.user},' \
               f' счёт: {self.score},' \
               f' линий: {self.lines},' \
               f' уровень {self.level}.'

    class Meta:
        verbose_name = 'Игровой счёт тетриса'
        verbose_name_plural = 'Игровые счета тетриса'


class MatchThreeScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField('Счёт')
    level = models.IntegerField('Уровень')
    date = models.DateTimeField(auto_now=True, blank=True, verbose_name='Дата')

    @classmethod
    def create(cls, request):
        return cls(
            user=request.user,
            score=request.GET.get('score'),
            level=request.GET.get('level')
        )

    def __str__(self):
        return f'Игрок: {self.user},' \
               f' счёт: {self.score},' \
               f' уровень {self.level}.'

    class Meta:
        verbose_name = 'Игровой счёт "Три в ряд"'
        verbose_name_plural = 'Игровые счета "Три в ряд"'
