from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    date = models.DateTimeField(auto_now=True, blank=True, verbose_name='Дата')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if self.__class__.objects.filter(name=self.name).exists():
            # Объект уже существует в базе данных, обновляем только поле date
            self.__class__.objects.filter(name=self.name).update(date=timezone.now())
        else:
            super().save(*args, **kwargs)
