from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)
    banned_users = models.ManyToManyField(User, related_name="banned_users", blank=True)
    is_private = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name="allowed_users", blank=True)
    pinned_message = models.OneToOneField("Message", on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name="pinned_to_room")

    def __str__(self):
        return f"Room({self.name} {self.host})"

    @database_sync_to_async
    def is_user_banned(self, user):
        return self.banned_users.filter(id=user.id).exists()

    @database_sync_to_async
    def ban_user(self, user):
        if is_new_user_banned := not self.is_user_id_banned(user.id):
            self.banned_users.add(user)
            self.current_users.remove(user)
        return is_new_user_banned

    def is_user_id_banned(self, user_id):
        return self.banned_users.filter(id=user_id).exists()

    @database_sync_to_async
    def rename(self, room_name, user):
        if Room.objects.filter(name=room_name).exists():
            return ["Комната с таким именем уже существует"]
        elif self.host == user or user.is_superuser:
            self.name = room_name
            self.save()
            return []
        else:
            return ["Ошибка доступа"]

    @database_sync_to_async
    def set_pinned_message(self, pinned_message_id):
        if pinned_message_id is None:
            self.pinned_message = None
        else:
            try:
                message = Message.objects.get(id=int(pinned_message_id))
                if message.room == self:
                    self.pinned_message = message
                else:
                    return ["Сообщение не из этого чата"]
            except Message.DoesNotExist:
                return ["Сообщение отсутствует на сервере"]
        self.save()
        return []


class Message(models.Model):
    room = models.ForeignKey("chat.Room", on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    reply_to = models.ForeignKey("Message", on_delete=models.SET_NULL, blank=True, null=True, related_name="replies")

    def __str__(self):
        return f"Message({self.user} {self.room})"

    @database_sync_to_async
    def update(self, message_id, text, user):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return ["Сообщение не найдено"]
        if message.user == user or user.is_superuser:
            message.text = text
            message.is_edited = True
            message.save()
        else:
            return ["Отказано в доступе"]

    @database_sync_to_async
    def remove(self, message_id, user):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return ["Сообщение не найдено"]
        if message.user == user or user.is_superuser:
            message.delete()
        else:
            return ["Отказано в доступе"]
