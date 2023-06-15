from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .services.timer import start_timer, elapsed_time


class GameScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.IntegerField('Сложность')
    elapsed_time = models.IntegerField('Затраченное время')
    hidden_word = models.CharField('Слово', max_length=10)
    attempts = models.IntegerField('Попытки')
    date = models.DateTimeField(auto_now=True, blank=True, verbose_name='Дата')

    def __str__(self):
        return f'Игрок: {self.user},' \
               f' сложность: {self.difficulty},' \
               f' время: {self.elapsed_time},' \
               f' загаданное слово {self.hidden_word}.'

    class Meta:
        verbose_name = 'Игровой счёт'
        verbose_name_plural = 'Игровые счета'

    @classmethod
    def copy_of_current_session(cls, source_obj):
        # Создание нового экземпляра TargetModel на основе объекта SourceModel
        game_score_obj = cls()
        game_score_obj.user = source_obj.user
        game_score_obj.difficulty = source_obj.difficulty
        game_score_obj.hidden_word = source_obj.hidden_word
        game_score_obj.attempts = len(source_obj.entered_words_list)
        game_score_obj.elapsed_time = int(elapsed_time(source_obj.start_time))
        return game_score_obj


class EnterWords(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    enter_word = models.CharField('Введённое слово', max_length=10)

    def __str__(self):
        return f'Введённое слово {self.enter_word}.'

    class Meta:
        verbose_name = 'Введённое слово'
        verbose_name_plural = 'Введённые слова'


class CurrentSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.IntegerField('difficulty', default=5)
    start_time = models.DecimalField('Время начала', default=0, max_digits=30, decimal_places=7)
    hidden_word = models.CharField('Слово', default='старт', max_length=10)
    entered_words_list = ArrayField(models.CharField(max_length=10), default=list)
    coincidences_list = ArrayField(models.CharField(max_length=200), default=list)
    notice = models.CharField('уведомление', default="", max_length=255)

    @classmethod
    def create(cls, user):
        return cls(user=user,
                   start_time=start_timer())

    def __str__(self):
        return f'Игрок: {self.user},' \
               f' сложность: {self.difficulty},' \
               f' время: {self.start_time},' \
               f' загаданное слово: {self.hidden_word},' \
               f' введённые слова: {self.entered_words_list},' \
               f' раскрашенное слово: {self.coincidences_list},' \
               f' уведомление: {self.notice}.'

    class Meta:
        verbose_name = 'Текущая сессия'
        verbose_name_plural = 'Текущие сессии'


class UserAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.CharField('Данные об устройстве', default="", max_length=255)

    @classmethod
    def create(cls, request):
        return cls(user=request.user,
                   agent=request.META.get('HTTP_USER_AGENT'))

    def __str__(self):
        return f'Игрок: {self.user},' \
               f' Данные об устройстве: {self.agent}.'

    class Meta:
        verbose_name = 'Данные об устройстве'
        verbose_name_plural = 'Данные об устройстве'
