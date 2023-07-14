from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)
    baned_users = models.ManyToManyField(User, related_name="baned_users", blank=True)
    is_private = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, related_name="allowed_users", blank=True)
    pinned_message = models.OneToOneField("Message", on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name="pinned_to_room")

    def __str__(self):
        return f"Room({self.name} {self.host})"


class Message(models.Model):
    room = models.ForeignKey("chat.Room", on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    reply_to = models.ForeignKey("Message", on_delete=models.SET_NULL, blank=True, null=True, related_name="replies")

    def __str__(self):
        return f"Message({self.user} {self.room})"
