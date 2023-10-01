from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)

from .models import Round
from .serializers import RoundSerializer
from .service import pole_chudes_game


class GameConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
    lookup_field = "pk"

    # async def websocket_connect(self, message):
    #     if self.scope['user'].is_authenticated:
    #         print(message)
    #         await super().websocket_connect(message)
    #     else:
    #         print(message)
    #         await self.close()

    async def disconnect(self, code):
        if hasattr(self, "room_subscribe"):
            await self.remove_user_from_room(self.room_subscribe)
        await super().disconnect(code)

    @action()
    async def join_room(self, pk, **kwargs):
        if self.scope['user'].is_authenticated:
            room: Round = await self.get_room(pk=pk)
            self.room_subscribe = pk
            await self.add_user_to_room(pk)

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)

    @action()
    async def rotate_wheel(self, pk, **kwargs):
        room: Round = await self.get_room(pk)
        await database_sync_to_async(pole_chudes_game.rotate_wheel)(room)

    @action()
    async def check_letter(self, pk, letter, **kwargs):
        room: Round = await self.get_room(pk)
        await database_sync_to_async(pole_chudes_game.check_letter)(letter, room)

    @action()
    async def check_full_word(self, pk, full_word, **kwargs):
        room: Round = await self.get_room(pk)
        await database_sync_to_async(pole_chudes_game.check_full_word)(full_word, room)

    async def update_users(self, event: dict):
        await self.send_json(event)

    @database_sync_to_async
    def get_room(self, pk: int) -> Round:
        return Round.objects.get(pk=pk)

    @database_sync_to_async
    def remove_user_from_room(self, pk, user=None):
        if user is None:
            user = self.scope["user"]

    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: User = self.scope["user"]
        # if not user.current_rooms.filter(pk=self.room_subscribe).exists():
        #     user.current_rooms.add(Round.objects.get(pk=pk))

    async def send_if_errors(self, action, errors):
        if errors:
            await self.send_json({"action": action, "errors": errors})
