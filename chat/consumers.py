from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from djangochannelsrestframework import mixins
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)

from .models import Room, Message
from .serializers import MessageSerializer, RoomSerializer, UserSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    async def websocket_connect(self, message):
        if self.scope['user'].is_authenticated:
            await super().websocket_connect(message)
        else:
            await self.close()

    async def add_group(self, name: str):
        await super().add_group(name)
        await self.send_current_users(name)

    async def remove_group(self, name: str):
        await super().remove_group(name)
        await self.send_current_users(name)

    async def disconnect(self, code):
        if hasattr(self, "room_subscribe"):
            await self.remove_user_from_room(self.room_subscribe)
        await super().disconnect(code)

    @action()
    async def join_room(self, pk, **kwargs):
        if self.scope['user'].is_authenticated:
            self.room_subscribe = pk
            await self.add_user_to_room(pk)
            await self.notify_users()

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)
        await self.notify_users()

    @action()
    async def create_message(self, message, **kwargs):
        room: Room = await self.get_room(pk=self.room_subscribe)
        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=self.scope["user"],
            text=message
        )

    @action()
    async def rename_room(self, room_name, **kwargs):
        room_name = ' '.join(room_name.strip().split())
        room_name = room_name[0].upper() + room_name[1:]
        room_exist = await database_sync_to_async(Room.objects.filter(name=room_name).exists)()
        if room_exist:
            await self.send_json({
                "action": "update",
                "errors": ["Комната с таким именем уже существует"]})
        else:
            await self.rename_room_at_bd(room_name)

    @action()
    async def set_pinned_message(self, pinned_message_id, **kwargs):
        await self.set_pinned_message_room_at_bd(pinned_message_id)

    @action()
    async def subscribe_to_messages_in_room(self, pk, **kwargs):
        await self.message_activity.subscribe(room=pk)

    @action()
    async def delete_message(self, message_id, **kwargs):
        await self.delete_message_from_bd(message_id=message_id)

    @action()
    async def edit_message(self, message_id, text, **kwargs):
        await self.update_message_at_bd(message_id=message_id, text=text)

    @action()
    async def update_current_users(self, **kwargs):
        room: Room = await self.get_room(self.room_subscribe)
        await self.send_json({'current_users': await self.current_users(room)})
        await self.notify_users()

    @model_observer(Message)
    async def message_activity(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: Message, **kwargs):
        yield f'room__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    @message_activity.serializer
    def message_activity(self, instance: Message, action, **kwargs):
        return dict(data=MessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'action': 'update_users',
                    'type': 'update_users',
                    'group': group,
                    'current_users': await self.current_users(room)
                }
            )

    async def send_current_users(self, group):
        room: Room = await self.get_room(self.room_subscribe)
        await self.channel_layer.group_send(
            group,
            {
                'action': 'update_users',
                'type': 'update_users',
                'group': group,
                'current_users': await self.current_users(room)
            }
        )

    async def update_users(self, event: dict):
        await self.send_json(event)

    @database_sync_to_async
    def get_room(self, pk: int) -> Room:
        return Room.objects.get(pk=pk)

    @database_sync_to_async
    def current_users(self, room: Room):
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, room, user_name=None):
        if user_name is None:
            self.scope["user"].current_rooms.remove(room)
        else:
            try:
                user = User.objects.get(user_name=user_name)
                user.current_rooms.remove(room)
            except User.DoesNotExist:
                self.send_json({"errors": ["Пользователь не найден"]})

    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: User = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))

    @database_sync_to_async
    def delete_message_from_bd(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return
        if message.user == self.scope["user"] or self.scope["user"].is_superuser:
            message.delete()

    @database_sync_to_async
    def update_message_at_bd(self, message_id, text):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return
        if message.user == self.scope["user"] or self.scope["user"].is_superuser:
            message.text = text
            message.is_edited = True
            message.save()

    @database_sync_to_async
    def rename_room_at_bd(self, room_name):
        try:
            room = Room.objects.get(pk=self.room_subscribe)
            if room.host == self.scope["user"] or self.scope["user"].is_superuser:
                room.name = room_name
                room.save()
            else:
                self.send_json({"errors": ["Ошибка доступа"]})
        except Room.DoesNotExist:
            return

    @database_sync_to_async
    def set_pinned_message_room_at_bd(self, pinned_message_id):
        try:
            room = Room.objects.get(pk=self.room_subscribe)
            if pinned_message_id is None:
                room.pinned_message = None
            else:
                message = Message.objects.get(id=int(pinned_message_id))
                if message.room == room:
                    room.pinned_message = message
                else:
                    self.send_json({"errors": ["Сообщение не из этого чата"]})
                    return
            room.save()
        except Room.DoesNotExist:
            print('Room.DoesNotExist')
            return
        except Message.DoesNotExist:
            self.send_json({"errors": ["Сообщение отсутствует на сервере"]})
            return


class UserConsumer(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.PatchModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DeleteModelMixin,
    GenericAsyncAPIConsumer,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
