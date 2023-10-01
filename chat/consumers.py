from channels.db import database_sync_to_async
from django.contrib.auth.models import User
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
            room: Room = await self.get_room(pk=pk)
            user_is_banned = await room.is_user_banned(self.scope['user'])
            if user_is_banned:
                await self.send_json({
                    "action": "join_room",
                    "errors": ["Вас добавили в бан-лист"]})
                await self.close(code=1000)
            else:
                self.room_subscribe = pk
                await self.add_user_to_room(pk)
                await self.notify_users()

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)
        await self.notify_users()

    @action()
    async def ban_users(self, ban_list, **kwargs):
        room: Room = await self.get_room(pk=self.room_subscribe)
        is_new_users_banned = False
        for user_id in ban_list:
            try:
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                is_new_users_banned = is_new_users_banned or await room.ban_user(user)
            except User.DoesNotExist:
                await self.send_json({
                    "action": "ban_users",
                    "errors": ["Пользователь не найден"]})
        if is_new_users_banned:
            await room.asave()

    @action()
    async def create_message(self, message, **kwargs):
        room: Room = await self.get_room(pk=self.room_subscribe)
        user_is_banned = await room.is_user_banned(self.scope['user'])
        if user_is_banned:
            await self.send_json({
                "action": "create_message",
                "errors": ["Вас добавили в бан-лист"]})
            await self.close(code=1000)
        else:
            await database_sync_to_async(Message.objects.create)(
                room=room,
                user=self.scope["user"],
                text=message
            )

    @action()
    async def rename_room(self, room_name, **kwargs):
        room_name = ' '.join(room_name.strip().split())
        room_name = room_name[0].upper() + room_name[1:]
        room: Room = await self.get_room(pk=self.room_subscribe)
        await self.send_if_errors("update", await room.rename(room_name, self.scope["user"]))

    @action()
    async def set_pinned_message(self, pinned_message_id, **kwargs):
        room: Room = await self.get_room(pk=self.room_subscribe)
        await self.send_if_errors("update", await room.set_pinned_message(pinned_message_id))

    @action()
    async def subscribe_to_messages_in_room(self, pk, **kwargs):
        await self.message_activity.subscribe(room=pk)

    @action()
    async def delete_message(self, message_id, **kwargs):
        await self.send_if_errors("delete", await Message.delete(message_id, self.scope["user"]))

    @action()
    async def edit_message(self, message_id, text, **kwargs):
        await self.send_if_errors("update", await Message.update(message_id, text, self.scope["user"]))

    @action()
    async def update_current_users(self, **kwargs):
        room: Room = await self.get_room(self.room_subscribe)
        await self.send_json({'current_users': await self.current_users(room)})

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
        if hasattr(self, 'room_subscribe'):
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
    def remove_user_from_room(self, pk, user=None):
        if user is None:
            user = self.scope["user"]
        room = Room.objects.get(pk=pk)
        room.current_users.remove(user)
        room.save()

    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: User = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))

    async def send_if_errors(self, action, errors):
        if errors:
            await self.send_json({"action": action, "errors": errors})

# class UserConsumer(
#     mixins.ListModelMixin,
#     mixins.RetrieveModelMixin,
#     # mixins.PatchModelMixin,
#     # mixins.UpdateModelMixin,
#     # mixins.CreateModelMixin,
#     # mixins.DeleteModelMixin,
#     GenericAsyncAPIConsumer,
# ):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
