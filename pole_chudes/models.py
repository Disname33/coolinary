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


class Round(models.Model):
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    word_mask = models.CharField('Маска ответа', max_length=20)
    is_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Проверка на новый объект
            self.riddle = Riddle.objects.order_by('?').first()
            self.word_mask = '*' * len(self.riddle.word)
        super(Round, self).save(*args, **kwargs)

    def next_riddle(self, *args, **kwargs):
        self.riddle = Riddle.objects.order_by('?').first()
        self.word_mask = '*' * len(self.riddle.word)
        self.is_complete = False
        super(Round, self).save(*args, **kwargs)

# class Result(models.Model):
#     player = models.ForeignKey(User, on_delete=models.CASCADE)
#     round = models.ForeignKey(Round, on_delete=models.CASCADE)
#     score = models.IntegerField(default=0)
