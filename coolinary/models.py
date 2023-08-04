import os

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


def get_avatar_filename(instance, filename):
    if filename is None:
        return None
    else:
        user_id = instance.user.id
        ext = os.path.splitext(filename)[1]
        return f'avatars/{user_id}{ext}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])])
    birthday = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Страна')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Город')
    gender = models.CharField(max_length=8, null=True, blank=True, choices=[('m', 'Мужской'), ('f', 'Женский')],
                              verbose_name='Пол')
    display_option = models.CharField(max_length=10, choices=[('nickname', 'Никнейм'), ('fullname', 'Имя и фамилия')],
                                      default='nickname', verbose_name='Показывать')

    def __str__(self):
        return self.user.username
