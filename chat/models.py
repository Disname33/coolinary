from django.contrib.auth.models import User
from django.db import models


# class Room(models.Model):
#     name = models.CharField(max_length=255, null=False, blank=False, unique=True)
#     host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
#     current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Room({self.name} {self.host})"


class Message(models.Model):
    # room = models.ForeignKey("chat.Room", on_delete=models.CASCADE, related_name="messages")
    room = models.CharField(max_length=100, null=False, verbose_name='Комната')
    text = models.TextField(max_length=500, verbose_name='Текст')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages", verbose_name='Отправитель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    def __str__(self):
        return f"Message({self.sender} {self.room}): {self.text}"
