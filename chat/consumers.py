import json
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        if isinstance(self.user, AnonymousUser):
            await self.close()
        elif self.room_name.startswith("pm_") and self.user.username not in self.room_name.split("_")[1:]:
            await self.close()
        else:

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            await self.join_room()
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": f"К нам присоединился(ась) {self.user}"}
            )

    async def join_room(self):
        last_20_messages = await self.get_last_message()
        # Отправка последних 20 сообщений пользователю
        for message in last_20_messages:
            await self.send(message)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": f"{self.scope['user']} покинул(а) чат"}
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text_message = text_data_json["message"]
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message",
                                   "sender": str(self.scope['user']),
                                   "message": text_message,
                                   'created_at': datetime.now().isoformat()}
        )
        await self.save_new_message(text_message=text_message)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        created_at = ''
        if "created_at" in event:
            created_at = event["created_at"]
        if "sender" in event:
            sender = event["sender"]
        else:
            sender = "Системное сообщение"
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,
                                              'sender': sender,
                                              'created_at': created_at}))

    @database_sync_to_async
    def get_last_message(self):
        text_data_list = []
        last_20_messages = Message.objects.filter(room=self.room_name).order_by('-created_at')[:20]
        # Отправка последних 20 сообщений пользователю
        for message in reversed(last_20_messages):
            text_data_list.append(json.dumps({"type": "chat_message",
                                              "message": message.text,
                                              "sender": message.sender.username,
                                              'created_at': message.created_at.isoformat()}))
        return text_data_list

    @database_sync_to_async
    def save_new_message(self, text_message):
        message = Message(room=self.scope["url_route"]["kwargs"]["room_name"],
                          text=text_message,
                          sender=self.scope['user'])
        message.save()
