import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


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
        # Получаем последние 10 сообщений отсортированных по дате создания
        # messages = Message.objects.order_by('-created_at')[:10]

        # Сериализуем сообщения в JSON
        # serializer = MessageSerializer(messages, many=True)
        # serialized_messages = serializer.data

        # Отправляем сообщения пользователю через WebSocket
        # await self.send(text_data=serialized_messages)
        await self.send(text_data=json.dumps({"type": "chat_message",
                                              "message": f"Проверка связи в комнате",
                                              "sender": "Предыдущие сообщения"}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": f"{self.scope['user']} покинул(а) чат"}
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "sender": str(self.scope['user']), "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        if "sender" in event:
            sender = event["sender"]
        else:
            sender = "Системное сообщение"
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, 'sender': sender}))
